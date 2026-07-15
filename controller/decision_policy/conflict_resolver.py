"""
conflict_resolver.py
"""
def resolve_conflicts(matched_rules: list) -> dict:
    if not matched_rules:
        return None
        
    # Priority DESC, policy_rule_id ASC
    sorted_rules = sorted(
        matched_rules, 
        key=lambda r: (-int(r.get("priority", 0)), r.get("policy_rule_id", ""))
    )
    return sorted_rules[0]
