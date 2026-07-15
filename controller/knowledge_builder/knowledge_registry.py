"""
knowledge_registry.py
Maintains knowledge_registry.json. Append-only.
Never overwrites previous records.
"""

import json
import os
from datetime import datetime
from knowledge_schema import KNOWLEDGE_BUILDER_VERSION

REGISTRY_VERSION = "1.0.0"
REGISTRY_FILENAME = "knowledge_registry.json"

class KnowledgeRegistry:
    def __init__(self, registry_dir="knowledge"):
        self.registry_dir = registry_dir
        self.registry_path = os.path.join(registry_dir, REGISTRY_FILENAME)
        os.makedirs(registry_dir, exist_ok=True)
        self._registry = self._load()

    def _load(self):
        if os.path.exists(self.registry_path):
            with open(self.registry_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {
            "registry_version": REGISTRY_VERSION,
            "created_at":       datetime.now().strftime("%Y%m%d_%H%M%S"),
            "total_records":    0,
            "records":          []
        }

    def _save(self):
        with open(self.registry_path, "w", encoding="utf-8") as f:
            json.dump(self._registry, f, indent=4)

    def register(self, record_data):
        """
        Appends a new knowledge record to the registry.
        Returns True if new, False if duplicate.
        """
        required_fields = [
            "knowledge_id", "evaluation_id", "experiment_id",
            "knowledge_directory", "knowledge_status", "knowledge_version", "decision"
        ]
        for field in required_fields:
            if field not in record_data:
                raise ValueError(f"[KnowledgeRegistry] Missing required field: {field}")

        # Duplicate guard by knowledge_id
        for r in self._registry["records"]:
            if r["knowledge_id"] == record_data["knowledge_id"]:
                return False

        self._registry["records"].append(record_data)
        self._registry["total_records"]  = len(self._registry["records"])
        self._registry["last_updated"]   = datetime.now().strftime("%Y%m%d_%H%M%S")
        self._save()
        return True

    @property
    def total_records(self):
        return self._registry["total_records"]

    @property
    def version(self):
        return self._registry["registry_version"]

    @property
    def registry_path_value(self):
        return self.registry_path
