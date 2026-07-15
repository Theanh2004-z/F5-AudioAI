"""
retrieval_loader.py
"""
import os
import json
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from retrieval_schema import RetrievalError, ERROR_REGISTRY_CORRUPTED, ERROR_DATASET_VERSION_MISMATCH, ERROR_INDEX_NOT_FOUND

def resolve_dataset_version(learning_registry_path: str, requested_version: str = None) -> tuple:
    """Loads learning_registry.json and resolves dataset version, dataset path, and index."""
    if not os.path.exists(learning_registry_path):
        raise RetrievalError(ERROR_REGISTRY_CORRUPTED, "learning_registry.json not found")
        
    try:
        with open(learning_registry_path, "r", encoding="utf-8") as f:
            registry = json.load(f)
    except Exception as e:
        raise RetrievalError(ERROR_REGISTRY_CORRUPTED, f"Failed to parse learning_registry.json: {e}")
        
    records = registry.get("records", [])
    if not records:
        raise RetrievalError(ERROR_REGISTRY_CORRUPTED, "learning_registry.json has no records")
        
    target_record = None
    if requested_version and requested_version != "LATEST":
        for r in records:
            if r.get("dataset_version") == requested_version:
                target_record = r
                break
        if not target_record:
            raise RetrievalError(ERROR_DATASET_VERSION_MISMATCH, f"Version {requested_version} not found in registry")
    else:
        target_record = records[-1]
        
    base_dir = os.path.dirname(learning_registry_path)
    index_path = os.path.join(base_dir, "learning_index.json")
    if not os.path.exists(index_path):
        raise RetrievalError(ERROR_INDEX_NOT_FOUND, "learning_index.json not found in registry directory")
        
    try:
        with open(index_path, "r", encoding="utf-8") as f:
            index_data = json.load(f)
    except Exception as e:
        raise RetrievalError(ERROR_INDEX_NOT_FOUND, f"Failed to parse learning_index.json: {e}")
        
    dataset_path = os.path.join(base_dir, target_record["dataset_path"])
    
    return target_record["dataset_version"], dataset_path, index_data
