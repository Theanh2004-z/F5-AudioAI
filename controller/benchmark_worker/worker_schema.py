"""
worker_schema.py
Schema definitions, benchmark statuses, versions, and artifact contracts for Stage 9.
No optimization. No AI. Deterministic constants only.
"""

WORKER_VERSION = "1.0.0"

# Valid statuses for a benchmark run
BENCHMARK_STATUSES = {
    "PENDING":     "Execution loaded but benchmark not yet started.",
    "RUNNING":     "Benchmark pipeline is currently executing.",
    "COMPLETED":   "Benchmark finished successfully.",
    "FAILED":      "Benchmark failed due to an error.",
    "VALIDATED":   "Benchmark artifacts successfully validated.",
    "INVALID":     "Benchmark finished but failed artifact validation.",
    "SKIPPED":     "Execution already benchmarked or not VALIDATED."
}

# The contract of expected artifacts per benchmark run
EXPECTED_ARTIFACTS = [
    "report.json",
    "feature_vector.npy",
    "dashboard.png",
    "benchmark_manifest.json",
    "benchmark_runtime.json"
]
