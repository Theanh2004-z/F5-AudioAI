"""
rule_registry.py
Static Rule Registry. Each rule is a data record only.
Rule evaluator reads from this registry. No hardcoded rule IDs in logic modules.
"""

RULE_ENGINE_VERSION = "1.0.0"
RULE_REGISTRY_VERSION = "1.0.0"

RULES = [
    {
        "rule_id": "RULE-001",
        "rule_name": "CORRUPTED_BENCHMARK_GUARD",
        "rule_version": "1.0.0",
        "description": "If the benchmark is marked corrupted, the decision is immediately INVALID.",
        "enabled": True
    },
    {
        "rule_id": "RULE-002",
        "rule_name": "NAN_GUARD",
        "rule_version": "1.0.0",
        "description": "If any NaN value is detected in feature deltas, the decision is FAIL.",
        "enabled": True
    },
    {
        "rule_id": "RULE-003",
        "rule_name": "INF_GUARD",
        "rule_version": "1.0.0",
        "description": "If any Inf value is detected in feature deltas, the decision is FAIL.",
        "enabled": True
    },
    {
        "rule_id": "RULE-004",
        "rule_name": "ERROR_OUTCOME_GUARD",
        "rule_version": "1.0.0",
        "description": "If any feature evaluation returns ERROR outcome, the decision is INVALID.",
        "enabled": True
    },
    {
        "rule_id": "RULE-005",
        "rule_name": "ALL_DEGRADED_FAIL",
        "rule_version": "1.0.0",
        "description": "If there are degraded features and zero improved features, the decision is FAIL.",
        "enabled": True
    },
    {
        "rule_id": "RULE-006",
        "rule_name": "ALL_IMPROVED_PASS",
        "rule_version": "1.0.0",
        "description": "If all features are improved and none are degraded, the decision is PASS.",
        "enabled": True
    },
    {
        "rule_id": "RULE-007",
        "rule_name": "MIXED_PARTIAL_PASS",
        "rule_version": "1.0.0",
        "description": "If there are both improved and degraded features, the decision is PARTIAL_PASS.",
        "enabled": True
    },
    {
        "rule_id": "RULE-008",
        "rule_name": "ALL_UNCHANGED_FAIL",
        "rule_version": "1.0.0",
        "description": "If all features are unchanged (no improvement, no degradation), the decision is FAIL.",
        "enabled": True
    }
]

def get_all_rules():
    return RULES

def get_enabled_rules():
    return [r for r in RULES if r.get("enabled", False)]
