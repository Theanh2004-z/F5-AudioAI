"""
retrieval_schema.py
"""
RETRIEVAL_SCHEMA_VERSION = "1.0.0"

class RetrievalError(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message
        super().__init__(f"[{code}] {message}")

ERROR_INDEX_NOT_FOUND = "INDEX_NOT_FOUND"
ERROR_DATASET_VERSION_MISMATCH = "DATASET_VERSION_MISMATCH"
ERROR_RECORD_NOT_FOUND = "RECORD_NOT_FOUND"
ERROR_REGISTRY_CORRUPTED = "REGISTRY_CORRUPTED"
ERROR_SCHEMA_VERSION_MISMATCH = "SCHEMA_VERSION_MISMATCH"
