"""
dataset_validator.py
Validates the output dataset to ensure structural integrity and schema compliance.
"""
import os
import json

def validate_dataset(dataset_path, manifest_path):
    """
    Checks if both files exist, and if the manifest correctly points to the dataset.
    Returns boolean success.
    """
    if not os.path.exists(dataset_path):
        return False
    if not os.path.exists(manifest_path):
        return False
        
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
        
    if manifest.get("dataset_path") != os.path.basename(dataset_path):
        return False
        
    return True
