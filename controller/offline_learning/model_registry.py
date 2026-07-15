"""
model_registry.py
"""
import os
import json

class ModelRegistry:
    def __init__(self, registry_dir: str = "dataset/models"):
        self.registry_dir = registry_dir
        self.registry_path = os.path.join(registry_dir, "model_registry.json")
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
            
    def register(self, session_id, winner, stats, manifest_path):
        self.data["records"].append({
            "learning_session_id": session_id,
            "best_model": winner,
            "metrics": stats.get(winner, {}),
            "manifest_path": os.path.basename(manifest_path)
        })
        self._save()
