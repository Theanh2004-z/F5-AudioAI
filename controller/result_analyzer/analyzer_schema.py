"""
analyzer_schema.py
Schema definitions, status codes, and artifact contracts for Stage 10.
No optimization, scoring, or AI. Deterministic constants only.
"""

ANALYZER_VERSION = "1.0.0"

# Valid statuses for an analysis run
ANALYSIS_STATUSES = {
    "PENDING":     "Benchmark loaded but analysis not yet started.",
    "RUNNING":     "Analysis pipeline is currently executing.",
    "COMPLETED":   "Analysis finished successfully.",
    "FAILED":      "Analysis failed due to an error.",
    "VALIDATED":   "Analysis artifacts successfully validated.",
    "INVALID":     "Analysis finished but failed artifact validation.",
    "SKIPPED":     "Benchmark already analyzed or not VALIDATED."
}

# The contract of expected artifacts per analysis run
EXPECTED_ARTIFACTS = [
    "analysis.json",
    "feature_delta.json",
    "quality_summary.json",
    "analysis_manifest.json",
    "runtime.json"
]
