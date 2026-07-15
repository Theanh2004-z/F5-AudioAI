"""
curation_rule_registry.py
Centralizes all deterministic validation rules. Hardcoding rules inside validators is strictly forbidden.
"""

RULES = {
    "RULE-001": "Required Traceability Fields",
    "RULE-002": "Dataset Schema Version Match",
    "RULE-003": "Duplicate Sample ID",
    "RULE-004": "Null Feature Deltas",
    "RULE-005": "Invalid Decision Value",
    "RULE-006": "Checksum Match"
}

def get_rule_desc(rule_id):
    return RULES.get(rule_id, "Unknown Rule")
