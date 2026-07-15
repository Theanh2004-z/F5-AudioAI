"""
inference_schema.py
"""
INFERENCE_SCHEMA_VERSION = "1.0.0"

class InferenceError(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message
        super().__init__(f"[{code}] {message}")

ERROR_REGISTRY_RESOLUTION_FAILED = "REGISTRY_RESOLUTION_FAILED"
ERROR_ARTIFACT_MISSING = "ARTIFACT_MISSING"
ERROR_PIPELINE_TRANSFORM_FAILED = "PIPELINE_TRANSFORM_FAILED"
ERROR_PREDICTION_FAILED = "PREDICTION_FAILED"
