"""
anomaly_detector.py
Detects numerical anomalies (NaN, Inf, Outliers) and missing features.
Deterministic flagging only.
"""

import numpy as np

def detect_anomalies(feature_delta_dict, quality_summary_dict):
    """
    Scans the extracted deltas and metrics for anomalies.
    
    Args:
        feature_delta_dict: Output from feature_delta_calculator.
        quality_summary_dict: Output from quality_summarizer.
        
    Returns:
        dict: A dictionary flagging specific anomalies found.
    """
    anomalies = {
        "has_nan": False,
        "has_inf": False,
        "missing_features": False,
        "corrupted_benchmark": False,
        "outlier_count": 0,
        "details": []
    }
    
    # 1. Check Corrupted Benchmark
    if quality_summary_dict.get("status_flag") != "success":
        anomalies["corrupted_benchmark"] = True
        anomalies["details"].append("Benchmark report status is not success.")
        
    if quality_summary_dict.get("extracted_metrics_count", 0) == 0:
        anomalies["missing_features"] = True
        anomalies["details"].append("Quality summary contains 0 metrics.")
        
    # 2. Check Deltas for NaN / Inf
    abs_deltas = feature_delta_dict.get("absolute_deltas", [])
    
    for idx, val in enumerate(abs_deltas):
        if np.isnan(val):
            anomalies["has_nan"] = True
            anomalies["details"].append(f"NaN found at feature index {idx}.")
        elif np.isinf(val):
            anomalies["has_inf"] = True
            anomalies["details"].append(f"Inf found at feature index {idx}.")
            
        # 3. Simple Outlier Detection (Z-score approach is too complex/ML, we use a simple hard threshold)
        # Assuming normalized features, a delta > 10.0 is likely a catastrophic outlier.
        elif abs(val) > 10.0:
            anomalies["outlier_count"] += 1
            anomalies["details"].append(f"Outlier (abs_delta > 10.0) at feature index {idx}: {val}")
            
    return anomalies
