"""
learning_manifest.py
"""
import os
import json
import hashlib
import time

def generate_manifest(records, dataset_id, dataset_version, dataset_path, output_dir):
    with open(dataset_path, "rb") as f:
        checksum = hashlib.sha256(f.read()).hexdigest()
        
    manifest = {
        "learning_dataset_id": dataset_id,
        "dataset_version": dataset_version,
        "dataset_path": os.path.basename(dataset_path),
        "checksum": checksum,
        "total_learning_records": len(records),
        "created_at": time.time()
    }
    
    path = os.path.join(output_dir, f"learning_manifest_v{dataset_version}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=4)
        
    return manifest, path
