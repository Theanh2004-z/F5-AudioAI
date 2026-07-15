"""
executor_schema.py
Schema definitions, execution statuses, versions, and constants for Stage 8.
No optimization. No AI. Deterministic execution constants only.
"""

EXECUTOR_VERSION = "1.0.0"

# Valid statuses for an execution run
EXECUTION_STATUSES = {
    "PENDING":     "Experiment is loaded but not yet started.",
    "RUNNING":     "F5-TTS inference is currently executing.",
    "COMPLETED":   "Execution finished successfully.",
    "FAILED":      "Execution failed due to an error.",
    "VALIDATED":   "Execution artifacts successfully validated.",
    "INVALID":     "Execution finished but failed artifact validation."
}

# The contract of expected artifacts per execution
EXPECTED_ARTIFACTS = [
    "generated.wav",
    "execution_manifest.json",
    "runtime.json",
    "stdout.log",
    "stderr.log"
]

# Output schema for execution_report.json
EXECUTION_REPORT_SCHEMA_DOC = {
    "metadata": {
        "executor_version": "Version of the Experiment Executor.",
        "timestamp":        "Report generation timestamp."
    },
    "summary": {
        "total_experiments_loaded":   "Number of experiments in the plan.",
        "total_executions_attempted": "Number of actual inference runs.",
        "total_completed":            "Number of executions finished without exceptions.",
        "total_failed":               "Number of executions that threw exceptions.",
        "total_validated":            "Number of executions passing artifact validation."
    },
    "execution_records": [
        {
            "execution_id":    "UUID of this specific execution run.",
            "experiment_id":   "UUID of the planned experiment.",
            "status":          "Final status (VALIDATED, INVALID, FAILED).",
            "execution_dir":   "Path to the execution artifact folder.",
            "duration_sec":    "Runtime duration in seconds.",
            "error_message":   "Exception message if failed, else null."
        }
    ]
}
