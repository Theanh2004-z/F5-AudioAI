"""
feature_selector.py
"""
import pandas as pd
import sys
import os
from sklearn.preprocessing import StandardScaler
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from learning_schema import OfflineLearningError, ERROR_DATASET_TOO_SMALL, ERROR_CLASS_IMBALANCE

def process_features(X_raw, y_raw):
    if len(X_raw) < 10:
        raise OfflineLearningError(ERROR_DATASET_TOO_SMALL, "Dataset requires at least 10 samples.")
        
    if len(set(y_raw)) < 2:
        raise OfflineLearningError(ERROR_CLASS_IMBALANCE, "Dataset requires at least 2 distinct classes in target variable.")

    flattened = []
    for r in X_raw:
        row = {}
        for k, v in r.get("metadata", {}).items():
            row[f"meta_{k}"] = v
        for feat, stats in r.get("feature_statistics", {}).items():
            for stat_k, stat_v in stats.items():
                if isinstance(stat_v, (int, float)):
                    row[f"stat_{feat}_{stat_k}"] = stat_v
        flattened.append(row)
        
    df = pd.DataFrame(flattened)
    df = pd.get_dummies(df, drop_first=True)
    df = df.fillna(0)
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df)
    
    return X_scaled, df.columns.tolist(), y_raw
