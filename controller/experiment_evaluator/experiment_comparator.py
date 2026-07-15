"""
experiment_comparator.py
Compares feature deltas against baseline thresholds.
No reasoning or causality inference. Deterministic comparisons only.
"""

import json
import os

def compare_features(analysis_dir):
    """
    Reads feature_delta.json and quality_summary.json from the analysis directory
    and returns a flattened structure comparing them to a zero-delta baseline.
    
    Args:
        analysis_dir: Path to the analysis directory.
        
    Returns:
        list: A list of feature comparison dicts.
    """
    feature_delta_path = os.path.join(analysis_dir, "feature_delta.json")
    
    if not os.path.exists(feature_delta_path):
        raise FileNotFoundError(f"[ExperimentComparator] {feature_delta_path} not found.")
        
    with open(feature_delta_path, "r", encoding="utf-8") as f:
        deltas = json.load(f)
        
    abs_deltas = deltas.get("absolute_deltas", [])
    rel_deltas = deltas.get("relative_deltas", [])
    
    comparisons = []
    
    for idx, (abs_val, rel_val) in enumerate(zip(abs_deltas, rel_deltas)):
        # Very simple deterministic baseline comparison
        comparisons.append({
            "feature_index": idx,
            "absolute_delta": abs_val,
            "relative_delta": rel_val,
            "is_zero": abs_val == 0.0,
            "is_positive": abs_val > 0.0,
            "is_negative": abs_val < 0.0
        })
        
    return comparisons
