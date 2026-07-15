"""
quality_evaluator.py
Evaluates individual metrics to determine IMPROVED, UNCHANGED, or DEGRADED.
Deterministic rules only based on feature profiles. No AI.
"""

from feature_profile_registry import get_feature_profile, DIR_LOWER_IS_BETTER, DIR_HIGHER_IS_BETTER, DIR_CLOSER_IS_BETTER

def evaluate_quality(comparisons, analysis_data):
    """
    Evaluates the quality of each feature based on simple deterministic thresholds.
    
    Args:
        comparisons: List of dicts from experiment_comparator.
        analysis_data: Data loaded from analysis.json (contains anomalies).
        
    Returns:
        list: Evaluation results for each feature.
    """
    evaluations = []
    anomalies = analysis_data.get("anomalies_detected", {})
    
    for comp in comparisons:
        idx = comp["feature_index"]
        abs_delta = comp["absolute_delta"]
        rel_delta = comp["relative_delta"]
        
        prof = get_feature_profile(idx)
        imp_thresh = prof["improved_threshold"]
        deg_thresh = prof["degraded_threshold"]
        direction = prof["direction"]
        
        if anomalies.get("has_nan") or anomalies.get("has_inf") or anomalies.get("corrupted_benchmark"):
            outcome = "ERROR"
        else:
            # Evaluate using specific profiles
            if direction == DIR_CLOSER_IS_BETTER:
                if abs(rel_delta) <= imp_thresh:
                    outcome = "IMPROVED" if abs(rel_delta) < (imp_thresh * 0.5) else "UNCHANGED"
                elif abs(rel_delta) >= deg_thresh:
                    outcome = "DEGRADED"
                else:
                    outcome = "UNCHANGED"
            elif direction == DIR_LOWER_IS_BETTER:
                if rel_delta <= -imp_thresh:
                    outcome = "IMPROVED"
                elif rel_delta >= deg_thresh:
                    outcome = "DEGRADED"
                else:
                    outcome = "UNCHANGED"
            elif direction == DIR_HIGHER_IS_BETTER:
                if rel_delta >= imp_thresh:
                    outcome = "IMPROVED"
                elif rel_delta <= -deg_thresh:
                    outcome = "DEGRADED"
                else:
                    outcome = "UNCHANGED"
            else:
                outcome = "UNCHANGED"
            
            # Anomalies override bounds if severe (outlier)
            if anomalies.get("outlier_count", 0) > 0 and abs(rel_delta) > 1.0:
                outcome = "DEGRADED"
                
        evaluations.append({
            "feature_index": idx,
            "outcome": outcome,
            "relative_delta_abs": abs(rel_delta)
        })
        
    return evaluations
