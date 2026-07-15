"""
experiment_planner.py — Main Orchestrator (Stage 7)

INPUT (all required):
  --reasoning    : path to reasoning_report.json
  --registry     : path to parameter_registry.json
  --space        : path to parameter_space.json
  --database     : path to experiment_database.json (or sample_registry.json)

OUTPUT:
  experiment_plan.json  (written to --output_dir)

Pipeline:
  1. Load 4 input files
  2. hypothesis_ranker      → Filters & ranks hypotheses by confidence and safety
  3. experiment_generator   → Generates PARAMETER_SWEEP and BOUNDARY_PROBE plans
  4. plan_validator         → Checks uniqueness, bounds, and ranges
  5. experiment_scheduler   → Assigns priority and sorts
  6. Assemble experiment_plan.json
  7. Export

The engine NEVER produces:
  - Parameter selections (only sweeps/ranges)
  - Optimization metrics
  - Calls to F5-TTS
"""

import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from planner_schema       import PLANNER_VERSION
from hypothesis_ranker    import rank_hypotheses
from experiment_generator import generate_experiments
from plan_validator       import validate_experiments
from experiment_scheduler import schedule_experiments

PLAN_FILENAME = "experiment_plan.json"


def run_experiment_planner(
    reasoning_path,
    registry_path,
    space_path,
    database_path,
    output_dir="."
):
    """
    Runs the full Experiment Planner pipeline.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # ── 1. Load inputs ────────────────────────────────────────────────────
    def _load(path, label):
        if not os.path.exists(path):
            raise FileNotFoundError(f"[ExperimentPlanner] {label} not found: {path}")
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    reasoning_report   = _load(reasoning_path, "reasoning_report.json")
    parameter_registry = _load(registry_path,  "parameter_registry.json")
    parameter_space    = _load(space_path,     "parameter_space.json")
    # database is loaded for completeness, though future scheduling logic
    # might use it to avoid repeating historically failed sweeps.
    experiment_database = _load(database_path, "experiment_database.json")

    print(f"  Loaded reasoning_report  : {reasoning_path}")
    print(f"  Loaded parameter_registry: {registry_path}")
    print(f"  Loaded parameter_space   : {space_path}")
    print(f"  Loaded experiment_database:{database_path}")

    lever_hypotheses = reasoning_report.get("lever_hypotheses", [])
    total_received   = len(lever_hypotheses)
    
    # ── 2. Rank and Filter Hypotheses ─────────────────────────────────────
    ranked, skipped, rank_warnings = rank_hypotheses(
        lever_hypotheses,
        parameter_registry
    )
    print(f"  Hypotheses ranked          : {len(ranked)} (skipped {len(skipped)})")

    # ── 3. Generate Candidate Experiments ─────────────────────────────────
    candidate_experiments = []
    gen_warnings = []

    reasoning_report_name = os.path.basename(reasoning_path)

    for hyp in ranked:
        exps, g_warn = generate_experiments(
            hyp, parameter_space, parameter_registry, reasoning_report_name
        )
        candidate_experiments.extend(exps)
        gen_warnings.extend(g_warn)
    
    print(f"  Candidate experiments gen. : {len(candidate_experiments)}")

    # ── 4. Validate Plans ──────────────────────────────────────────────────
    passed, rejected, val_warnings = validate_experiments(
        candidate_experiments, parameter_space
    )
    print(f"  Experiments passed valid.  : {len(passed)} (rejected {len(rejected)})")

    # ── 5. Schedule (Order) ────────────────────────────────────────────────
    scheduled, sched_warnings = schedule_experiments(passed)

    # ── 6. Assemble Report ─────────────────────────────────────────────────
    all_warnings = rank_warnings + gen_warnings + val_warnings + sched_warnings

    risk_counts = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "EXTREME_RISK": 0}
    family_counts = {}
    cost_counts = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "EXTREME": 0}
    duplicate_count = 0
    total_deps = 0

    for e in scheduled:
        # Risk
        r = e.get("risk_level", "UNKNOWN")
        if r in risk_counts:
            risk_counts[r] += 1
        
        # Family
        f = e.get("experiment_family", "UNKNOWN")
        family_counts[f] = family_counts.get(f, 0) + 1

        # Cost
        c = e.get("cost_estimation", {}).get("estimated_runtime", "UNKNOWN")
        if c in cost_counts:
            cost_counts[c] += 1
        
        # Duplicate
        if e.get("execution_status") == "DUPLICATE":
            duplicate_count += 1
        
        # Dependencies
        total_deps += len(e.get("dependencies", []))

    avg_deps = total_deps / len(scheduled) if scheduled else 0.0

    plan = {
        "metadata": {
            "planner_version": PLANNER_VERSION,
            "timestamp":       timestamp,
            "input_files": {
                "reasoning_report":   os.path.basename(reasoning_path),
                "parameter_registry": os.path.basename(registry_path),
                "parameter_space":    os.path.basename(space_path),
                "experiment_database":os.path.basename(database_path)
            }
        },
        "summary": {
            "total_hypotheses_received":   total_received,
            "hypotheses_above_threshold":  len(ranked),
            "total_experiments_planned":   len(scheduled),
            "total_experiments_skipped":   len(rejected),
            "total_warnings":              len(all_warnings)
        },
        "planner_statistics": {
            "family_breakdown":         family_counts,
            "risk_breakdown":           risk_counts,
            "cost_breakdown":           cost_counts,
            "duplicate_count":          duplicate_count,
            "average_dependency_count": round(avg_deps, 2)
        },
        "planned_experiments": scheduled,
        "validation": {
            "passed":   [e["experiment_id"] for e in scheduled],
            "rejected": rejected
        },
        "warnings": all_warnings
    }

    # ── 7. Export ──────────────────────────────────────────────────────────
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, PLAN_FILENAME)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(plan, f, indent=4, ensure_ascii=False)

    print(f"\n✅ experiment_plan.json → {out_path}")
    return plan


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="F5-TTS Experiment Planner")
    p.add_argument("--reasoning",  required=True, help="Path to reasoning_report.json")
    p.add_argument("--registry",   required=True, help="Path to parameter_registry.json")
    p.add_argument("--space",      required=True, help="Path to parameter_space.json")
    p.add_argument("--database",   required=True, help="Path to experiment_database.json")
    p.add_argument("--output_dir", default=".",   help="Output directory")
    args = p.parse_args()

    run_experiment_planner(
        args.reasoning,
        args.registry,
        args.space,
        args.database,
        args.output_dir
    )
