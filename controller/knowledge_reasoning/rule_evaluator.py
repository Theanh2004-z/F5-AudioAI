"""
rule_evaluator.py
"""
def resolve_field(record: dict, path: str):
    parts = path.split('.')
    current = record
    for part in parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None
    return current

def evaluate_condition(record: dict, condition: dict) -> bool:
    field_path = condition.get("field")
    operator = condition.get("operator")
    target_val = condition.get("value")
    
    actual_val = resolve_field(record, field_path)
    if actual_val is None:
        return False
        
    if operator == "IN":
        return actual_val in target_val
    elif operator == "==":
        return actual_val == target_val
    elif operator == "!=":
        return actual_val != target_val
    elif operator == ">=":
        return actual_val >= target_val
    elif operator == "<=":
        return actual_val <= target_val
    elif operator == ">":
        return actual_val > target_val
    elif operator == "<":
        return actual_val < target_val
    return False

def evaluate_rule(record: dict, rule: dict) -> bool:
    conditions = rule.get("conditions", [])
    if not conditions:
        return False
    for cond in conditions:
        if not evaluate_condition(record, cond):
            return False
    return True
