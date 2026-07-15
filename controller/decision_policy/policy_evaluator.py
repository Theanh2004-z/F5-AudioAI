"""
policy_evaluator.py
"""
def evaluate_policy_rule(finding: dict, policy_rule: dict) -> bool:
    trigger_finding_types = policy_rule.get("trigger_finding_type", [])
    finding_type = finding.get("finding_type")
    
    if finding_type in trigger_finding_types:
        return True
    return False
