"""
rule_evaluator.py
Applies enabled rules from the Rule Registry to produce a final decision.
No rule IDs are hardcoded in the decision logic — all read from rule_registry.
"""

from rule_registry import get_enabled_rules

def evaluate_decision(evaluations, analysis_data):
    """
    Iterates enabled rules in priority order and returns the first matching decision.
    
    Args:
        evaluations: Output from quality_evaluator.
        analysis_data: The analysis.json dictionary.
        
    Returns:
        str: "PASS", "PARTIAL_PASS", "FAIL", or "INVALID"
    """
    anomalies = analysis_data.get("anomalies_detected", {})
    outcomes  = [e["outcome"] for e in evaluations]

    improved_count = outcomes.count("IMPROVED")
    degraded_count = outcomes.count("DEGRADED")
    error_count    = outcomes.count("ERROR")

    enabled_rules  = {r["rule_id"]: r for r in get_enabled_rules()}

    # Rules are evaluated in strict priority order.
    # Guard rules (INVALID/FAIL) always checked before outcome rules (PASS/PARTIAL_PASS).

    if "RULE-001" in enabled_rules and anomalies.get("corrupted_benchmark"):
        return "INVALID"

    if "RULE-002" in enabled_rules and anomalies.get("has_nan"):
        return "FAIL"

    if "RULE-003" in enabled_rules and anomalies.get("has_inf"):
        return "FAIL"

    if "RULE-004" in enabled_rules and error_count > 0:
        return "INVALID"

    if "RULE-005" in enabled_rules and degraded_count > 0 and improved_count == 0:
        return "FAIL"

    if "RULE-006" in enabled_rules and improved_count > 0 and degraded_count == 0:
        return "PASS"

    if "RULE-007" in enabled_rules and improved_count > 0 and degraded_count > 0:
        return "PARTIAL_PASS"

    if "RULE-008" in enabled_rules:
        return "FAIL"  # All unchanged

    return "INVALID"  # Fallback if all rules disabled
