"""
reasoning_engine.py — Main Orchestrator (Stage 6, Revised)

INPUT (all required):
  --observation    : path to observation_report.json
  --confidence     : path to confidence_report.json
  --normalized     : path to normalized_feature_difference.json
  --graph          : path to knowledge_graph.json

OUTPUT:
  reasoning_report.json  (written to --output_dir)

Pipeline:
  1. Load 4 input files
  2. evidence_collector   → evidence_map, load_warnings
  3. graph_reasoner       → feature_lever_index
  4. hypothesis_builder   → feature_observations, feature_hypotheses, unknowns
  5. lever_aggregator     → lever_hypotheses (LEVER-CENTRIC aggregation)
  6. Assemble reasoning_report
  7. Export reasoning_report.json

The engine NEVER produces:
  - Parameter values
  - Parameter deltas
  - Tuning recommendations
  - Optimization signals

It only produces:
  - Feature observations
  - Candidate hypotheses (lever name + evidence + confidence)
  - Unknowns (unresolved observations)
  - Warnings (data quality issues)
"""

import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from reasoning_schema    import REASONING_ENGINE_VERSION
from evidence_collector  import collect_evidence
from graph_reasoner      import build_feature_lever_index
from hypothesis_builder  import build_hypotheses
from lever_aggregator    import aggregate_by_lever

REPORT_FILENAME = "reasoning_report.json"


def run_reasoning_engine(
    observation_path,
    confidence_path,
    normalized_path,
    graph_path,
    output_dir="."
):
    """
    Runs the full Reasoning Engine pipeline.

    Args:
        observation_path : str — path to observation_report.json
        confidence_path  : str — path to confidence_report.json
        normalized_path  : str — path to normalized_feature_difference.json
        graph_path       : str — path to knowledge_graph.json
        output_dir       : str — directory to write reasoning_report.json

    Returns:
        dict — the full reasoning report
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # ── 1. Load inputs ────────────────────────────────────────────────────
    def _load(path, label):
        if not os.path.exists(path):
            raise FileNotFoundError(f"[ReasoningEngine] {label} not found: {path}")
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    observation_report = _load(observation_path, "observation_report.json")
    confidence_report  = _load(confidence_path,  "confidence_report.json")
    normalized_report  = _load(normalized_path,  "normalized_feature_difference.json")
    knowledge_graph    = _load(graph_path,        "knowledge_graph.json")

    print(f"  Loaded observation_report  : {observation_path}")
    print(f"  Loaded confidence_report   : {confidence_path}")
    print(f"  Loaded normalized_diff     : {normalized_path}")
    print(f"  Loaded knowledge_graph     : {graph_path}")

    # ── 2. Collect evidence ───────────────────────────────────────────────
    evidence_map, collect_warnings = collect_evidence(
        observation_report, confidence_report, normalized_report
    )
    print(f"  Evidence packets collected : {len(evidence_map)}")

    # ── 3. Build feature-lever index from graph ───────────────────────────
    feature_lever_index = build_feature_lever_index(knowledge_graph)
    print(f"  Graph features indexed     : {len(feature_lever_index)}")

    # ── 4. Build feature-level hypotheses ──────────────────────────────────
    feature_observations, feature_hypotheses, unknowns, build_warnings = build_hypotheses(
        evidence_map, feature_lever_index
    )
    print(f"  Feature hypotheses         : {len(feature_hypotheses)}")
    print(f"  Unknowns                   : {len(unknowns)}")

    # ── 5. Aggregate into lever-centric hypotheses ────────────────────────
    lever_hypotheses, agg_warnings = aggregate_by_lever(feature_hypotheses, evidence_map)
    print(f"  Lever hypotheses (agg)     : {len(lever_hypotheses)}")
    conflicts_total = sum(lh["conflict_count"] for lh in lever_hypotheses)
    print(f"  Conflicting features total : {conflicts_total}")

    # ── 6. Assemble report ────────────────────────────────────────────────
    all_warnings = collect_warnings + build_warnings + agg_warnings

    report = {
        "metadata": {
            "version":   REASONING_ENGINE_VERSION,
            "timestamp": timestamp,
            "inputs": {
                "observation_report":            os.path.basename(observation_path),
                "confidence_report":             os.path.basename(confidence_path),
                "normalized_feature_difference": os.path.basename(normalized_path),
                "knowledge_graph":               os.path.basename(graph_path)
            },
            "summary": {
                "total_features_observed":   len(feature_observations),
                "total_feature_hypotheses":  len(feature_hypotheses),
                "total_lever_hypotheses":    len(lever_hypotheses),
                "total_unknowns":            len(unknowns),
                "total_conflicts_detected":  sum(lh["conflict_count"] for lh in lever_hypotheses),
                "total_warnings":            len(all_warnings)
            }
        },
        "feature_observations":  feature_observations,
        "feature_hypotheses":    feature_hypotheses,
        "lever_hypotheses":      lever_hypotheses,
        "unknowns":              unknowns,
        "warnings":              all_warnings
    }

    # ── 6. Export ─────────────────────────────────────────────────────────
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, REPORT_FILENAME)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4, ensure_ascii=False)

    print(f"\n✅ reasoning_report.json → {out_path}")
    return report


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="F5-TTS Reasoning Engine")
    p.add_argument("--observation",  required=True, help="Path to observation_report.json")
    p.add_argument("--confidence",   required=True, help="Path to confidence_report.json")
    p.add_argument("--normalized",   required=True, help="Path to normalized_feature_difference.json")
    p.add_argument("--graph",        required=True, help="Path to knowledge_graph.json")
    p.add_argument("--output_dir",   default=".",   help="Output directory")
    args = p.parse_args()

    run_reasoning_engine(
        args.observation,
        args.confidence,
        args.normalized,
        args.graph,
        args.output_dir
    )
