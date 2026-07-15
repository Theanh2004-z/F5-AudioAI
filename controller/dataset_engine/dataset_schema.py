"""
dataset_schema.py
Defines JSON schemas and constants for Stage 13: Dataset Consolidation.
"""

DATASET_ENGINE_VERSION = "1.0.0"
DATASET_SCHEMA_VERSION = "1.0.0"

EXPECTED_ARTIFACTS = [
    "dataset_registry.json",
    "dataset_report.json"
]

# Note: We won't strictly enforce schema checking in code unless required,
# but these variables serve as the contract.
