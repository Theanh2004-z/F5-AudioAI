"""
evaluator_schema.py
Schema definitions, status codes, and artifact contracts for Stage 11.
No AI. Deterministic rules only.
"""

EVALUATOR_VERSION = "1.0.0"

# Valid statuses for an evaluation run
EVALUATION_STATUSES = {
    "PENDING":     "Analysis loaded but evaluation not yet started.",
    "RUNNING":     "Evaluation pipeline is currently executing.",
    "COMPLETED":   "Evaluation finished successfully.",
    "FAILED":      "Evaluation failed due to an error.",
    "VALIDATED":   "Evaluation artifacts successfully validated.",
    "INVALID":     "Evaluation finished but failed artifact validation.",
    "SKIPPED":     "Analysis already evaluated or not VALIDATED."
}

# The contract of expected artifacts per evaluation run
EXPECTED_ARTIFACTS = [
    "evaluation.json",
    "scorecard.json",
    "decision.json",
    "evaluation_profile.json",
    "decision_explanation.json",
    "decision_trace.json",
    "rule_statistics.json",
    "evaluation_manifest.json",
    "runtime.json"
]

# Valid Quality Evaluator outcomes
QUALITY_OUTCOMES = ["IMPROVED", "UNCHANGED", "DEGRADED", "ERROR"]

# Valid Rule Evaluator decisions
DECISION_OUTCOMES = ["PASS", "PARTIAL_PASS", "FAIL", "INVALID"]
