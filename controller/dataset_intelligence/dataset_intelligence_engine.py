"""
dataset_intelligence_engine.py
"""
import os
import sys
import uuid
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from intelligence_loader import load_curated_dataset
from aggregator import aggregate_samples
from learning_builder import build_learning_records
from learning_manifest import generate_manifest
from learning_statistics import generate_statistics
from learning_index import generate_index
from learning_registry import LearningRegistry
from intelligence_logger import IntelligenceLogger

def build_learning_dataset(curation_registry_path, output_dir="dataset/intelligence"):
    logger = IntelligenceLogger()
    os.makedirs(output_dir, exist_ok=True)
    registry = LearningRegistry(output_dir)
    
    curated_samples, curation_latest, curation_manifest = load_curated_dataset(curation_registry_path)
    
    latest_learning = registry.get_latest()
    if latest_learning:
        parts = latest_learning.get("dataset_version", "1.0.0").split(".")
        new_version = f"{parts[0]}.{int(parts[1])+1}.0"
    else:
        new_version = "1.0.0"
        
    metadata_versions = {
        "dataset_version": new_version,
        "dataset_manifest_version": "UNKNOWN",
        "curation_version": curation_latest.get("dataset_version", "1.0.0"),
        "curation_manifest_version": curation_manifest.get("curated_dataset_version", "1.0.0"),
        "knowledge_snapshot_version": curation_manifest.get("source_dataset_id", "UNKNOWN")
    }
    
    aggregated_data = aggregate_samples(curated_samples)
    records = build_learning_records(aggregated_data, metadata_versions)
    
    dataset_id = f"LRN-DS-{uuid.uuid4().hex[:6].upper()}"
    dataset_filename = f"learning_dataset_v{new_version}.json"
    dataset_path = os.path.join(output_dir, dataset_filename)
    
    with open(dataset_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=4)
        
    manifest, manifest_path = generate_manifest(records, dataset_id, new_version, dataset_path, output_dir)
    
    generate_index(records, output_dir)
    generate_statistics(records, output_dir, metadata_versions)
    
    reg_entry = {
        "learning_dataset_id": dataset_id,
        "dataset_version": new_version,
        "dataset_path": dataset_filename,
        "manifest_path": os.path.basename(manifest_path),
        "checksum": manifest["checksum"],
        "total_learning_records": len(records),
        "status": "VALIDATED"
    }
    registry.register(reg_entry)
    
    return manifest
    
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", required=True)
    parser.add_argument("--output_dir", default="dataset/intelligence")
    args = parser.parse_args()
    build_learning_dataset(args.registry, args.output_dir)
