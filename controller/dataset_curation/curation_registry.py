"""
curation_registry.py
Single Source of Truth for curated datasets.
"""
import os
import json

class CurationRegistry:
    def __init__(self, registry_dir="dataset/curated"):
        self.registry_dir = registry_dir
        self.registry_path = os.path.join(registry_dir, "curation_registry.json")
        self.version = "1.0.0"
        self._load()
        
    def _load(self):
        if os.path.exists(self.registry_path):
            with open(self.registry_path, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        else:
            self.data = {"registry_version": self.version, "total_curations": 0, "records": []}
            self._save()
            
    def _save(self):
        os.makedirs(self.registry_dir, exist_ok=True)
        with open(self.registry_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4)
            
    def register(self, record):
        self.data["records"].append(record)
        self.data["total_curations"] = len(self.data["records"])
        self._save()
