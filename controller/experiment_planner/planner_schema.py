"""
planner_schema.py (Stage 7 Revision)
JSON schema definitions for Experiment Planner output.

No optimization. No parameter selection. No tuning.
"""

PLANNER_VERSION = "1.2.0"

# ── Field documentation ────────────────────────────────────────────────────────

EXPERIMENT_MANIFEST_DOC = {
    "experiment_id":           "Unique UUID identifier (e.g. EXP-a8c93b2f).",
    "parent_reasoning_report": "Filename of the reasoning report that triggered this plan.",
    "hypothesis_id":           "ID or name of the source hypothesis.",
    "target_lever":            "Name of the lever this experiment targets.",
    "experiment_type":         "Plan type: PARAMETER_SWEEP | BOUNDARY_PROBE | BASELINE_CHECK.",
    "objective":               "Human-readable description of what this experiment intends to observe.",
    "creation_timestamp":      "Timestamp of plan creation.",
    "planner_version":         "Version of the Experiment Planner.",
    "expected_outputs":        "List of expected outputs.",
    "execution_status":        "Status: PLANNED | RUNNING | COMPLETED | FAILED | CANCELLED.",
    "provenance":              "Tracking metadata (versions, sources).",
    "reproducibility":         "Runtime environments (OS, Python).",
    "expected_observations":   "List of feature names to observe.",
    "success_criteria":        "List of dicts {feature, expected_direction}.",
    "rollback_metadata":       "Dict containing rollback_policy.",
    "dependencies":            "List of coupled levers.",
    "risk_level":              "Safety classification: LOW | MEDIUM | HIGH | EXTREME.",
    "parameter_name":          "The parameter variable name.",
    "parameter_range":         "Ordered list of values to sweep.",
    "step_count":              "Number of discrete test points.",
    "schedule_priority":       "Scheduling priority integer. Lower = run earlier.",
    "experiment_fingerprint":  "SHA256 deterministic hash of experiment definition.",
    "duplicate_of":            "If status is DUPLICATE, points to original experiment_id.",
    "experiment_family":       "Logical family like CFG_EXPLORATION, SPEED_CALIBRATION.",
    "cost_estimation":         "Dict of estimated_runtime, estimated_gpu_memory, etc.",
    "execution_priority":      "Computed execution priority based on risk and cost.",
    "experiment_tags":         "List of searchable tag strings.",
    "retry_policy":            "Metadata dict for retry configuration.",
    "expected_artifacts":      "List of expected output artifact filenames."
}

# Status values
VALID_STATUSES = {"PLANNED", "RUNNING", "COMPLETED", "FAILED", "CANCELLED", "DUPLICATE"}

# Allowed experiment types
EXPERIMENT_TYPES = {
    "PARAMETER_SWEEP":  "Tests the lever across a uniform range of values.",
    "BOUNDARY_PROBE":   "Tests only the min and max bounds of a parameter.",
    "BASELINE_CHECK":   "Tests the lever at its default value for reference collection."
}

# Scheduling strategies
SCHEDULING_STRATEGIES = {
    "SAFETY_FIRST":     "Runs highest-safety experiments first to establish baselines.",
    "CONFIDENCE_FIRST": "Runs highest reasoning_confidence hypotheses first.",
    "ISOLATION_FIRST":  "Runs most isolated (low coupling) levers first."
}
