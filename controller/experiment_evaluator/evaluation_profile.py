"""
evaluation_profile.py
Generates evaluation_profile.json detailing feature improvements and degradations by importance.
"""

from feature_profile_registry import get_feature_profile

EVALUATION_PROFILE_VERSION = "1.0.0"

def generate_evaluation_profile(quality_evals):
    """
    Summarizes the feature evaluations into an evaluation profile.
    
    Args:
        quality_evals: Output from quality_evaluator.
        
    Returns:
        dict: The evaluation profile summary.
    """
    profile = {
        "total_features": len(quality_evals),
        "improved": 0,
        "unchanged": 0,
        "degraded": 0,
        "error": 0,
        "critical_features": [],
        "high_importance_features": [],
        "medium_importance_features": [],
        "low_importance_features": []
    }
    
    for eval_item in quality_evals:
        idx = eval_item["feature_index"]
        outcome = eval_item["outcome"]
        
        feature_prof = get_feature_profile(idx)
        importance = feature_prof.get("importance", "LOW")
        feature_name = feature_prof.get("feature", f"feature_{idx}")
        
        # Count outcomes
        if outcome == "IMPROVED":
            profile["improved"] += 1
        elif outcome == "UNCHANGED":
            profile["unchanged"] += 1
        elif outcome == "DEGRADED":
            profile["degraded"] += 1
        elif outcome == "ERROR":
            profile["error"] += 1
            
        # Group by importance
        record = {
            "feature": feature_name,
            "feature_index": idx,
            "outcome": outcome
        }
        
        if importance == "CRITICAL":
            profile["critical_features"].append(record)
        elif importance == "HIGH":
            profile["high_importance_features"].append(record)
        elif importance == "MEDIUM":
            profile["medium_importance_features"].append(record)
        else:
            profile["low_importance_features"].append(record)
            
    return profile
