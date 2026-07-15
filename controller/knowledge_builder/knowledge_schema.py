"""
knowledge_schema.py
Schema definitions, status codes, and artifact contracts for Stage 12 Knowledge Builder.
No AI, no ML, no scoring. Deterministic constants only.
"""

KNOWLEDGE_BUILDER_VERSION = "1.0.0"

# Only these evaluation decisions qualify for knowledge building
QUALIFYING_DECISIONS = ["PASS", "PARTIAL_PASS"]

# Decisions that are excluded
EXCLUDED_DECISIONS = ["FAIL", "INVALID"]

# Artifact contract per knowledge record directory
EXPECTED_ARTIFACTS = [
    "knowledge.json",
    "knowledge_profile.json",
    "knowledge_statistics.json",
    "knowledge_evidence.json",
    "knowledge_manifest.json",
    "runtime.json"
]

# Status codes for knowledge build runs
KNOWLEDGE_STATUSES = {
    "PENDING":   "Evaluation record loaded, knowledge not yet built.",
    "RUNNING":   "Knowledge extraction in progress.",
    "COMPLETED": "Knowledge record successfully built.",
    "FAILED":    "Knowledge build failed due to error.",
    "VALIDATED": "All artifacts present and traceability verified.",
    "INVALID":   "Build completed but artifact validation failed.",
    "SKIPPED":   "Evaluation already processed or not qualifying."
}
