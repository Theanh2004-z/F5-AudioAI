"""
experiment_generator.py (Stage 7 Revision)
Converts one ranked lever hypothesis into one or more candidate experiment plans.

Each plan is now a permanent Experiment Manifest containing:
- UUID-based ID
- Provenance and Reproducibility metadata
- Expected Observation Contract & Success Criteria
- Rollback Metadata & Dependency Lock
- Risk Annotation
"""

import math
import uuid
import platform
import json
import hashlib
from datetime import datetime
from planner_config import DEFAULT_STEP_COUNT, BOUNDARY_PROBE_STEP_COUNT, MAX_EXPERIMENTS_PER_LEVER
from planner_schema  import EXPERIMENT_TYPES, PLANNER_VERSION


def _linspace(lo, hi, n):
    """Returns n evenly spaced values from lo to hi, inclusive. Pure math."""
    if n < 2:
        return [round(lo, 4)]
    step = (hi - lo) / (n - 1)
    return [round(lo + i * step, 4) for i in range(n)]


def _get_bounds(lever_name, parameter_space):
    params = parameter_space.get("parameters", {})
    if lever_name not in params:
        return None, None
    constraints = params[lever_name].get("constraints", {})
    return constraints.get("min"), constraints.get("max")


def _generate_success_criteria(features, ranked_hypothesis):
    """
    Naively assigns 'unknown' expected_direction since the planner
    does not infer causality.
    """
    criteria = []
    for f in features:
        criteria.append({
            "feature": f,
            "expected_direction": "unknown"
        })
    return criteria


def _generate_fingerprint(definition_dict):
    """Generates a SHA256 deterministic hash of the experiment definition."""
    canonical = json.dumps(definition_dict, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(canonical.encode('utf-8')).hexdigest()


def _estimate_cost(step_count):
    """Returns qualitative cost estimations based on step count."""
    level = "LOW" if step_count <= 2 else "MEDIUM" if step_count <= 5 else "HIGH"
    return {
        "estimated_runtime": level,
        "estimated_gpu_memory": level,
        "estimated_disk_usage": level,
        "estimated_outputs": level
    }


def _compute_execution_priority(risk_level, runtime_level, dependency_count):
    """
    Computes a numerical priority (lower is earlier).
    Deterministic combination of risk, runtime, and deps.
    """
    risk_score = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "EXTREME": 4}.get(risk_level, 2)
    runtime_score = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "EXTREME": 4}.get(runtime_level, 2)
    # Higher risk or runtime delays the experiment
    return risk_score * 10 + runtime_score * 5 + dependency_count


def generate_experiments(
    ranked_hypothesis,
    parameter_space,
    parameter_registry,
    reasoning_report_name
):
    """
    Generates candidate experiment manifests from one ranked lever hypothesis.

    Args:
        ranked_hypothesis     : dict
        parameter_space       : dict
        parameter_registry    : list[dict]
        reasoning_report_name : str

    Returns:
        experiments  : list[dict]  — planned experiment manifests
        gen_warnings : list[str]
    """
    experiments  = []
    gen_warnings = []
    timestamp    = datetime.now().strftime("%Y%m%d_%H%M%S")

    lever    = ranked_hypothesis["lever"]
    reg      = ranked_hypothesis.get("_registry", {})
    conf     = ranked_hypothesis.get("reasoning_confidence", 0.0)
    support  = ranked_hypothesis.get("supporting_features", [])
    safety   = reg.get("safety", "UNKNOWN")

    lo, hi = _get_bounds(lever, parameter_space)
    if lo is None or hi is None:
        gen_warnings.append(
            f"[{lever}] Not found in parameter_space.json. Cannot generate sweep range."
        )
        return experiments, gen_warnings

    provenance = {
        "generated_by":             "experiment_planner",
        "reasoning_engine_version": "1.0.0",
        "knowledge_graph_version":  "1.0.0",
        "dataset_version":          "1.0.0"
    }

    reproducibility = {
        "python_version":           platform.python_version(),
        "os":                       platform.system(),
        "planner_version":          PLANNER_VERSION,
        "registry_version":         "1.0.0",
        "knowledge_graph_version":  "1.0.0",
        "feature_registry_version": "1.0.0"
    }

    rollback_policy = {
        "enabled": True,
        "restore_previous_parameters": True
    }
    
    # Retrieve dependencies if available in registry
    dependencies = []
    for r in parameter_registry:
        if r["name"] == lever:
            # Assuming parameter_registry might have coupling metadata
            # We don't have it natively, so default to empty
            pass

    retry_policy = {
        "max_retry": 2,
        "retry_on_failure": True,
        "retry_on_timeout": True
    }

    expected_artifacts = [
        "generated_audio.wav",
        "benchmark_report.json",
        "feature_vector.npy",
        "reasoning_report.json"
    ]

    family = f"{lever.upper()}_EXPLORATION"

    def _build_manifest(exp_type, objective, param_range):
        exp_id = f"EXP-{uuid.uuid4().hex[:8]}"
        step_count = len(param_range)
        cost_est = _estimate_cost(step_count)
        exec_prio = _compute_execution_priority(safety, cost_est["estimated_runtime"], len(dependencies))
        success_crits = _generate_success_criteria(support, ranked_hypothesis)

        tags = [lever, exp_type.lower(), safety.lower(), "tier1"]

        # Fingerprint definition: exclude UUIDs, timestamps, versions, etc.
        def_dict = {
            "hypothesis_id":         f"HYP-{lever}",
            "target_lever":          lever,
            "experiment_type":       exp_type,
            "parameter_range":       param_range,
            "expected_observations": support,
            "success_criteria":      success_crits
        }
        fingerprint = _generate_fingerprint(def_dict)

        return {
            "experiment_id":           exp_id,
            "experiment_fingerprint":  fingerprint,
            "experiment_family":       family,
            "parent_reasoning_report": reasoning_report_name,
            "hypothesis_id":           f"HYP-{lever}",
            "target_lever":            lever,
            "experiment_type":         exp_type,
            "objective":               objective,
            "creation_timestamp":      timestamp,
            "planner_version":         PLANNER_VERSION,
            "execution_status":        "PLANNED",
            "provenance":              provenance,
            "reproducibility":         reproducibility,
            "expected_observations":   support,
            "success_criteria":        success_crits,
            "rollback_metadata":       rollback_policy,
            "dependencies":            dependencies,
            "risk_level":              safety,
            "parameter_name":          lever,
            "parameter_range":         param_range,
            "step_count":              step_count,
            "reasoning_confidence":    conf,
            "safety_class":            safety,
            "cost_estimation":         cost_est,
            "execution_priority":      exec_prio,
            "experiment_tags":         tags,
            "retry_policy":            retry_policy,
            "expected_artifacts":      expected_artifacts
        }

    # ── Experiment 1: PARAMETER_SWEEP ────────────────────────────────────────
    sweep_range = _linspace(lo, hi, DEFAULT_STEP_COUNT)
    obj1 = (f"Sweep {lever} uniformly across its full range [{lo}, {hi}] "
            f"in {DEFAULT_STEP_COUNT} steps to observe acoustic feature responses.")
    experiments.append(_build_manifest("PARAMETER_SWEEP", obj1, sweep_range))

    # ── Experiment 2: BOUNDARY_PROBE (if budget allows) ──────────────────────
    if len(experiments) < MAX_EXPERIMENTS_PER_LEVER:
        boundary_range = _linspace(lo, hi, BOUNDARY_PROBE_STEP_COUNT)
        obj2 = (f"Probe only the minimum ({lo}) and maximum ({hi}) of {lever} "
                f"to establish hard boundary behaviour before full sweep.")
        experiments.append(_build_manifest("BOUNDARY_PROBE", obj2, boundary_range))

    return experiments, gen_warnings
