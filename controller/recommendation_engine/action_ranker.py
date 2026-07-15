"""
action_ranker.py
"""
def rank_actions(matched_actions):
    if not matched_actions:
        return None, []
        
    sorted_actions = sorted(matched_actions, key=lambda x: x.get("priority", 0), reverse=True)
    
    primary = sorted_actions[0]
    alternatives = [a["action_id"] for a in sorted_actions[1:]]
    
    return primary, alternatives
