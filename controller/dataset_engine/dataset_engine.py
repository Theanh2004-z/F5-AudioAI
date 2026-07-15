"""
dataset_engine.py
The single public orchestrator API for Stage 13 Dataset Consolidation.
"""

import os
import sys
import json
import time
import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from dataset_schema         import DATASET_ENGINE_VERSION, DATASET_SCHEMA_VERSION
from dataset_loader         import load_validated_knowledge, load_knowledge_data
from dataset_consolidator   import consolidate_sample
from dataset_builder        import build_dataset_samples
from dataset_registry       import DatasetRegistry
from dataset_version_manager import get_next_version
from dataset_manifest       import generate_manifest
from dataset_logger         import DatasetLogger
from dataset_validator      import validate_dataset

REPORT_FILENAME = "dataset_report.json"

def build_dataset(knowledge_registry_path, knowledge_base_dir, output_dir="dataset"):
    """
    Sole public API for generating an immutable dataset from Knowledge Base.
    """
    logger = DatasetLogger()
    os.makedirs(output_dir, exist_ok=True)
    registry = DatasetRegistry(output_dir)
    
    # Snapshot fallback retrieval
    snap_path = os.path.join(knowledge_base_dir, "knowledge_snapshot.json")
    snapshot_version = "UNKNOWN"
    if os.path.exists(snap_path):
        with open(snap_path, "r", encoding="utf-8") as f:
            snap = json.load(f)
            snapshot_version = snap.get("knowledge_snapshot_version", "UNKNOWN")

    try:
        # 1. Load validated records
        records = load_validated_knowledge(knowledge_registry_path)
        
        # 2. Consolidate raw samples
        raw_samples = []
        for rec in records:
            k_dir = rec.get("knowledge_directory", "")
            know_data, know_prof, know_evid, manifest = load_knowledge_data(k_dir)
            sample = consolidate_sample(rec, know_data, know_prof, know_evid, manifest)
            raw_samples.append(sample)
            
        # 3. Deduplicate (technical) and Deterministic Sort
        final_samples = build_dataset_samples(raw_samples)
        
        # 4. Resolve Version
        next_version = get_next_version(registry, DATASET_SCHEMA_VERSION)
        dataset_filename = f"dataset_v{next_version}.json"
        manifest_filename = f"dataset_manifest_v{next_version}.json"
        
        dataset_path = os.path.join(output_dir, dataset_filename)
        manifest_path = os.path.join(output_dir, manifest_filename)
        
        dataset_id = f"DS-{datetime.datetime.now().strftime('%Y%m%d')}-{str(int(time.time()))[-6:]}"
        
        # 5. Write Immutable Dataset
        with open(dataset_path, "w", encoding="utf-8") as f:
            json.dump(final_samples, f, indent=4)
            
        # 6. Generate & Write Manifest (incorporating checksum)
        manifest = generate_manifest(final_samples, dataset_id, next_version, dataset_path, snapshot_version)
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=4)
            
        # 7. Validate
        is_valid = validate_dataset(dataset_path, manifest_path)
        
        # 8. Register
        if is_valid:
            registry.register_dataset({
                "dataset_id": dataset_id,
                "dataset_version": next_version,
                "manifest_path": os.path.join(os.path.basename(output_dir), manifest_filename),
                "dataset_path": os.path.join(os.path.basename(output_dir), dataset_filename),
                "checksum": manifest["checksum"],
                "total_samples": len(final_samples),
                "created_at": manifest["created_at"],
                "status": "VALIDATED"
            })
            
        logger.stop(success=is_valid)
        
    except Exception as e:
        logger.stop(success=False, error=e)
        
    # Write Report
    report = {
        "metadata": {
            "dataset_engine_version": DATASET_ENGINE_VERSION,
            "timestamp": time.time()
        },
        "execution": {
            "duration_sec": logger.get_runtime(),
            "status": logger.status,
            "error": logger.error_message
        }
    }
    with open(os.path.join(output_dir, REPORT_FILENAME), "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)
        
    return report

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--knowledge_registry", required=True)
    parser.add_argument("--knowledge_base_dir", required=True)
    parser.add_argument("--output_dir", default="dataset")
    args = parser.parse_args()
    build_dataset(args.knowledge_registry, args.knowledge_base_dir, args.output_dir)
