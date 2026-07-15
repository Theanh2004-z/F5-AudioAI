"""
rule_statistics.py
Generates rule_statistics.json from a decision trace.
No scoring. No ranking. Pure counting.
"""

from rule_registry import get_all_rules, get_enabled_rules

RULE_STATISTICS_VERSION = "1.0.0"

def generate_rule_statistics(decision_trace):
    """
    Counts rule trigger states from the decision trace.
    
    Args:
        decision_trace: Output from decision_trace.generate_decision_trace()
        
    Returns:
        dict: Rule statistics.
    """
    all_rules     = get_all_rules()
    enabled_rules = get_enabled_rules()
    enabled_ids   = {r["rule_id"] for r in enabled_rules}

    triggered_rules = [t for t in decision_trace if t["triggered"]]
    skipped_rules   = [t for t in decision_trace if not t["triggered"]]

    return {
        "rule_statistics_version": RULE_STATISTICS_VERSION,
        "total_rules":     len(all_rules),
        "enabled_rules":   len(enabled_rules),
        "triggered_rules": len(triggered_rules),
        "skipped_rules":   len(skipped_rules),
        "failed_rules":    0,   # Reserved: for future rule execution errors
        "triggered_rule_ids": [t["rule_id"] for t in triggered_rules],
        "skipped_rule_ids":   [t["rule_id"] for t in skipped_rules]
    }
