"""
dataset_manifest.py
Generates the 1:1 linked manifest file for a dataset.
"""
import os
import json
import hashlib
import time

def generate_manifest(samples, dataset_id, dataset_version, dataset_path, snapshot_version):
    """
    Calculates checksum and aggregate metrics, returns manifest dictionary.
    """
    # Calculate checksum
    if os.path.exists(dataset_path):
        with open(dataset_path, "rb") as f:
            file_bytes = f.read()
            checksum = hashlib.sha256(file_bytes).hexdigest()
    else:
        # Fallback if generated before writing
        checksum = "pending"

    # Metrics
    experiments = set(s.get("experiment_id") for s in samples)
    evaluations = set(s.get("evaluation_id") for s in samples)
    knowledge_ids = set(s.get("knowledge_id") for s in samples)
    levers = set(s.get("lever") for s in samples)
    
    # Count features loosely by inspecting keys in observed_outcomes
    features = set()
    for s in samples:
        for f in s.get("observed_outcomes", {}).keys():
            features.add(f)
            
    manifest = {
        "dataset_id": dataset_id,
        "dataset_version": dataset_version,
        "dataset_path": os.path.basename(dataset_path),
        "total_samples": len(samples),
        "total_experiments": len(experiments),
        "total_evaluations": len(evaluations),
        "total_knowledge_records": len(knowledge_ids),
        "total_levers": len(levers),
        "total_features": len(features),
        "checksum": checksum,
        "created_at": time.time(),
        "source_knowledge_snapshot": snapshot_version
    }
    
    return manifest
