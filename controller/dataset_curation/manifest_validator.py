"""
manifest_validator.py
Generates a 1:1 manifest checking dataset checksum and version.
"""
import os
import json
import hashlib
import time

def generate_and_validate_manifest(curated_samples, dataset_id, dataset_version, dataset_path, source_id, output_dir):
    with open(dataset_path, "rb") as f:
        checksum = hashlib.sha256(f.read()).hexdigest()
        
    manifest = {
        "curated_dataset_id": f"CUR-{dataset_id}",
        "curated_dataset_version": dataset_version,
        "dataset_path": os.path.basename(dataset_path),
        "quality_report_path": "curation_quality_report.json",
        "source_dataset_id": source_id,
        "checksum": checksum,
        "total_samples": len(curated_samples),
        "schema_version": "1.0.0",
        "created_at": time.time()
    }
    
    manifest_path = os.path.join(output_dir, "curated_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=4)
        
    return manifest
