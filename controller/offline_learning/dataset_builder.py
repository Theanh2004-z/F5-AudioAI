"""
dataset_builder.py
"""
import json
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from learning_schema import OfflineLearningError, ERROR_ARTIFACT_CORRUPTED

def build_dataset(learning_dataset_path: str, reasoning_findings_path: str, decision_policy_path: str):
    try:
        with open(learning_dataset_path, "r", encoding="utf-8") as f:
            learning_dataset = json.load(f)
        with open(reasoning_findings_path, "r", encoding="utf-8") as f:
            reasoning_findings = json.load(f)
        with open(decision_policy_path, "r", encoding="utf-8") as f:
            decision_policy = json.load(f)
    except Exception:
        raise OfflineLearningError(ERROR_ARTIFACT_CORRUPTED, "Failed to read input triad.")

    records = {r["learning_record_id"]: r for r in learning_dataset}
    
    X_raw = []
    y_raw = []
    
    for pol in decision_policy.get("policies", []):
        lrn_ids = pol.get("traceability", {}).get("matched_learning_record_ids", [])
        ptype = pol.get("policy_type")
        for lrn in lrn_ids:
            if lrn in records:
                X_raw.append(records[lrn])
                y_raw.append(ptype)
                
    return X_raw, y_raw
