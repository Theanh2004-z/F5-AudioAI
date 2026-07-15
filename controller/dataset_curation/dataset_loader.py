"""
dataset_loader.py
Reads raw datasets from Stage 13.
"""
import os
import json

def load_source_dataset(stage13_registry_path):
    """Reads the authoritative path from stage 13 registry and loads the latest dataset."""
    if not os.path.exists(stage13_registry_path):
        raise FileNotFoundError(f"Source registry {stage13_registry_path} not found.")
        
    with open(stage13_registry_path, "r", encoding="utf-8") as f:
        registry = json.load(f)
        
    records = registry.get("records", [])
    if not records:
        raise ValueError("No datasets found in Stage 13 registry.")
        
    latest = records[-1]
    dataset_path = latest.get("dataset_path")
    # Resolve relative to registry path
    base_dir = os.path.dirname(stage13_registry_path)
    full_path = os.path.join(base_dir, os.path.basename(dataset_path))
    
    if not os.path.exists(full_path):
         full_path = os.path.join(base_dir, dataset_path)
         
    with open(full_path, "r", encoding="utf-8") as f:
        samples = json.load(f)
        
    return samples, latest
