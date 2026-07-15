"""
duplicate_detector.py
Checks for duplicate samples based on ID.
"""
def check_duplicate(sample, seen_sample_ids):
    """
    Triggers RULE-003
    """
    s_id = sample.get("sample_id")
    if not s_id or s_id in seen_sample_ids:
        return False, ["RULE-003"]
    seen_sample_ids.add(s_id)
    return True, []
