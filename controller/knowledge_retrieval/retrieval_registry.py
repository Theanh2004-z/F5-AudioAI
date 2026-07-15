"""
retrieval_registry.py
"""
import os
import json

class RetrievalRegistry:
    def __init__(self, registry_dir: str = "dataset/retrieval"):
        self.registry_dir = registry_dir
        self.registry_path = os.path.join(registry_dir, "retrieval_registry.json")
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
            
    def register(self, session_id: str, query_id: str, result_path: str, manifest_path: str, dataset_version: str, status: str, checksum: str):
        self.data["records"].append({
            "retrieval_session_id": session_id,
            "query_id": query_id,
            "result_path": os.path.basename(result_path),
            "manifest_path": os.path.basename(manifest_path),
            "resolved_dataset_version": dataset_version,
            "status": status,
            "checksum": checksum
        })
        self._save()
