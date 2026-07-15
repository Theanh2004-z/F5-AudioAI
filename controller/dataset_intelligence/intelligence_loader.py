"""
intelligence_loader.py
"""
import os
import json

def load_curated_dataset(curation_registry_path):
    if not os.path.exists(curation_registry_path):
        raise FileNotFoundError("curation_registry.json not found")
        
    with open(curation_registry_path, "r", encoding="utf-8") as f:
        registry = json.load(f)
        
    records = registry.get("records", [])
    if not records:
        raise ValueError("No records in curation_registry")
        
    latest = records[-1]
    dataset_path = latest.get("dataset_path")
    
    base_dir = os.path.dirname(curation_registry_path)
    full_path = os.path.join(base_dir, os.path.basename(dataset_path))
    if not os.path.exists(full_path):
        full_path = os.path.join(base_dir, dataset_path)
        
    with open(full_path, "r", encoding="utf-8") as f:
        samples = json.load(f)
        
    manifest_path = os.path.join(base_dir, os.path.basename(latest.get("manifest_path", "")))
    manifest = {}
    if os.path.exists(manifest_path):
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
            
    return samples, latest, manifest
