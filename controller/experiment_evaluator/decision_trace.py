"""
decision_trace.py
Generates decision_trace.json by recording which rules were triggered.
No AI. No NLP. Pure deterministic rule matching.
"""

from rule_registry import get_enabled_rules

def generate_decision_trace(evaluations, analysis_data):
    """
    Iterates enabled rules and records trigger status with reason and affected features.
    
    Args:
        evaluations: List of feature evaluation dicts from quality_evaluator.
        analysis_data: The analysis.json dictionary.
        
    Returns:
        list: A trace record per enabled rule.
    """
    anomalies = analysis_data.get("anomalies_detected", {})
    
    outcomes = [e["outcome"] for e in evaluations]
    improved_count  = outcomes.count("IMPROVED")
    degraded_count  = outcomes.count("DEGRADED")
    error_count     = outcomes.count("ERROR")

    improved_idxs   = [e["feature_index"] for e in evaluations if e["outcome"] == "IMPROVED"]
    degraded_idxs   = [e["feature_index"] for e in evaluations if e["outcome"] == "DEGRADED"]
    error_idxs      = [e["feature_index"] for e in evaluations if e["outcome"] == "ERROR"]

    trace = []

    for rule in get_enabled_rules():
        rid   = rule["rule_id"]
        rname = rule["rule_name"]
        triggered = False
        reason = ""
        affected_features = []

        if rid == "RULE-001":
            triggered = bool(anomalies.get("corrupted_benchmark"))
            reason = "Benchmark marked corrupted." if triggered else "Benchmark is clean."

        elif rid == "RULE-002":
            triggered = bool(anomalies.get("has_nan"))
            reason = "NaN detected in feature deltas." if triggered else "No NaN detected."

        elif rid == "RULE-003":
            triggered = bool(anomalies.get("has_inf"))
            reason = "Inf detected in feature deltas." if triggered else "No Inf detected."

        elif rid == "RULE-004":
            triggered = error_count > 0
            affected_features = error_idxs
            reason = f"{error_count} ERROR outcomes detected." if triggered else "No ERROR outcomes."

        elif rid == "RULE-005":
            triggered = degraded_count > 0 and improved_count == 0
            affected_features = degraded_idxs if triggered else []
            reason = f"{degraded_count} degraded, 0 improved." if triggered else "Not all-degraded."

        elif rid == "RULE-006":
            triggered = improved_count > 0 and degraded_count == 0
            affected_features = improved_idxs if triggered else []
            reason = f"{improved_count} improved, 0 degraded." if triggered else "Not all-improved."

        elif rid == "RULE-007":
            triggered = improved_count > 0 and degraded_count > 0
            affected_features = improved_idxs + degraded_idxs if triggered else []
            reason = f"{improved_count} improved and {degraded_count} degraded." if triggered else "Not mixed."

        elif rid == "RULE-008":
            triggered = improved_count == 0 and degraded_count == 0 and error_count == 0
            reason = "All features unchanged." if triggered else "Not all unchanged."

        trace.append({
            "rule_id":           rid,
            "rule_name":         rname,
            "rule_version":      rule["rule_version"],
            "triggered":         triggered,
            "reason":            reason,
            "affected_features": affected_features
        })

    return trace
