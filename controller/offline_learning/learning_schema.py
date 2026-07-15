"""
learning_schema.py
"""
LEARNING_SCHEMA_VERSION = "1.0.0"

class OfflineLearningError(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message
        super().__init__(f"[{code}] {message}")

ERROR_DATASET_TOO_SMALL = "DATASET_TOO_SMALL"
ERROR_CLASS_IMBALANCE = "CLASS_IMBALANCE"
ERROR_ARTIFACT_CORRUPTED = "ARTIFACT_CORRUPTED"
ERROR_NO_VALID_MODEL = "NO_VALID_MODEL"
