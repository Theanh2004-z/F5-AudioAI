"""
curation_schema.py
Defines exact JSON constants for Stage 14: Dataset Curation Engine.
"""

CURATION_SCHEMA_VERSION = "1.0.0"

VALID_STATUSES = {
    "VALID",
    "CORRUPTED",
    "INCOMPLETE",
    "INVALID_SCHEMA",
    "DUPLICATE_ID"
}
