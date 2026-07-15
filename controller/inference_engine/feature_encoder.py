"""
feature_encoder.py
"""
import sys
import os
import pandas as pd
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from inference_schema import InferenceError, ERROR_PIPELINE_TRANSFORM_FAILED

def encode_features(live_sample: dict, pipeline):
    try:
        flattened = {}
        for k, v in live_sample.get("metadata", {}).items():
            flattened[f"meta_{k}"] = v
        for feat, stats in live_sample.get("feature_statistics", {}).items():
            for stat_k, stat_v in stats.items():
                if isinstance(stat_v, (int, float)):
                    flattened[f"stat_{feat}_{stat_k}"] = stat_v
                    
        df = pd.DataFrame([flattened])
        
        X_encoded = pipeline.transform(df) if hasattr(pipeline, "transform") else df.values
        return X_encoded, df.columns.tolist()
    except Exception as e:
        raise InferenceError(ERROR_PIPELINE_TRANSFORM_FAILED, f"Failed to transform live sample: {e}")
