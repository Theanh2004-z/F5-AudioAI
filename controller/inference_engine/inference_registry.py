"""
inference_registry.py
"""
import os
import json

class InferenceRegistry:
    def __init__(self, registry_dir: str = "dataset/inference"):
        self.registry_dir = registry_dir
        self.registry_path = os.path.join(registry_dir, "inference_registry.json")
        self.version = "1.0.0"
        self._load()
        
    def _load(self):
        if os.path.exists(self.registry_path):
            with open(self.registry_path, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        else:
            self.data = {"registry_version": self.version, "records": []}
            
    def _save(self):
        os.makedirs(self.registry_dir, exist_ok=True)
        with open(self.registry_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4)
            
    def register(self, session_id, prediction_path, manifest_path):
        self.data["records"].append({
            "inference_session_id": session_id,
            "prediction_path": os.path.basename(prediction_path),
            "manifest_path": os.path.basename(manifest_path)
        })
        self._save()
