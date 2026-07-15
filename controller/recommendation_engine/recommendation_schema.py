"""
recommendation_schema.py
"""
RECOMMENDATION_SCHEMA_VERSION = "1.0.0"

class RecommendationError(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message
        super().__init__(f"[{code}] {message}")

ERROR_PREDICTION_CORRUPTED = "PREDICTION_CORRUPTED"
ERROR_RULES_MISSING = "RULES_MISSING"

ACTION_MANUAL_REVIEW = "ACT-MANUAL-REVIEW"
