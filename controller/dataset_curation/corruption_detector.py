"""
corruption_detector.py
Deterministically scans samples utilizing rules from the Rule Registry.
"""
def check_corruption(sample):
    """
    Triggers RULE-001 (Traceability), RULE-004 (Null Deltas), RULE-005 (Decision)
    """
    reasons = []
    # RULE-001
    traceability = sample.get("traceability", {})
    if not traceability or not sample.get("experiment_id") or not sample.get("knowledge_id"):
        reasons.append("RULE-001")
        
    # RULE-004
    if sample.get("feature_deltas") is None:
        reasons.append("RULE-004")
        
    # RULE-005
    if sample.get("decision") not in ["PASS", "FAIL", "PARTIAL_PASS"]:
        reasons.append("RULE-005")
        
    return len(reasons) == 0, reasons
