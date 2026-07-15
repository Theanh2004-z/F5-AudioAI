"""
policy_registry.py
"""
import os
import json

class PolicyRegistry:
    def __init__(self, registry_dir: str = "dataset/policy"):
        self.registry_dir = registry_dir
        self.registry_path = os.path.join(registry_dir, "decision_policy_registry.json")
        self.version = "1.0.0"
        self._load()
        
    def _load(self):
        if os.path.exists(self.registry_path):
            try:
                with open(self.registry_path, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except Exception:
                self.data = {"registry_version": self.version, "records": []}
        else:
            self.data = {"registry_version": self.version, "records": []}
            self._save()
            
    def _save(self):
        os.makedirs(self.registry_dir, exist_ok=True)
        with open(self.registry_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4)
            
    def register(self, session_id: str, policy_path: str, manifest_path: str, status: str, checksum: str):
        self.data["records"].append({
            "policy_session_id": session_id,
            "policy_path": os.path.basename(policy_path),
            "manifest_path": os.path.basename(manifest_path),
            "status": status,
            "checksum": checksum
        })
        self._save()
