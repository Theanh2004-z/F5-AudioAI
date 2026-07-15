"""
evaluation_statistics.py
Aggregates evaluation records into evaluation_statistics.json.
No scoring. No ranking. Pure histogram counting.
"""

def generate_evaluation_statistics(decision, profile):
    """
    Generates deterministic histograms for a single evaluation run.
    
    Args:
        decision: The final decision string.
        profile: The evaluation profile.
        
    Returns:
        dict: The statistics for this evaluation.
    """
    stats = {
        "decision_histogram": {
            "PASS": 1 if decision == "PASS" else 0,
            "PARTIAL_PASS": 1 if decision == "PARTIAL_PASS" else 0,
            "FAIL": 1 if decision == "FAIL" else 0,
            "INVALID": 1 if decision == "INVALID" else 0
        },
        "outcome_histogram": {
            "IMPROVED": profile.get("improved", 0),
            "UNCHANGED": profile.get("unchanged", 0),
            "DEGRADED": profile.get("degraded", 0),
            "ERROR": profile.get("error", 0)
        },
        "importance_histogram": {
            "CRITICAL": len(profile.get("critical_features", [])),
            "HIGH": len(profile.get("high_importance_features", [])),
            "MEDIUM": len(profile.get("medium_importance_features", [])),
            "LOW": len(profile.get("low_importance_features", []))
        },
        "averages": {
            "improved_ratio": 0.0,
            "degraded_ratio": 0.0,
            "unchanged_ratio": 0.0
        }
    }
    
    total_feats = profile.get("total_features", 1)
    if total_feats == 0: total_feats = 1
    
    stats["averages"]["improved_ratio"] = profile.get("improved", 0) / total_feats
    stats["averages"]["degraded_ratio"] = profile.get("degraded", 0) / total_feats
    stats["averages"]["unchanged_ratio"] = profile.get("unchanged", 0) / total_feats
    
    return stats
