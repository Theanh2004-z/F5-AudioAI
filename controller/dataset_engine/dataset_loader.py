"""
dataset_loader.py
Loads validated records from the knowledge registry and their corresponding artifacts.
"""

import os
import json

def load_validated_knowledge(knowledge_registry_path):
    """
    Loads all validated knowledge records from the knowledge registry.
    """
    if not os.path.exists(knowledge_registry_path):
        raise FileNotFoundError(f"Knowledge registry not found at {knowledge_registry_path}")
        
    with open(knowledge_registry_path, "r", encoding="utf-8") as f:
        registry = json.load(f)
        
    validated_records = []
    for record in registry.get("records", []):
        # Allow COMPLETED or VALIDATED based on how Stage 12 logs it.
        status = record.get("knowledge_status", "")
        if status in ["COMPLETED", "VALIDATED"]:
            validated_records.append(record)
            
    return validated_records

def load_knowledge_data(knowledge_dir):
    """
    Loads the necessary artifact files from a knowledge directory.
    """
    def _load(fname):
        path = os.path.join(knowledge_dir, fname)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    return (
        _load("knowledge.json"),
        _load("knowledge_profile.json"),
        _load("knowledge_evidence.json"),
        _load("knowledge_manifest.json")
    )
