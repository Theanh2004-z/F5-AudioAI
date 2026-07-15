"""
execution_registry.py
Maintains execution_registry.json.
Each execution must have a permanent immutable record.
Append only.
"""

import json
import os
from datetime import datetime
from executor_schema import EXECUTOR_VERSION

REGISTRY_VERSION = "1.0.0"
REGISTRY_FILENAME = "execution_registry.json"

class ExecutionRegistry:
    def __init__(self, registry_dir="executions"):
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
            "created_at": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "total_registered": 0,
            "records": []
        }
        
    def _save(self):
        with open(self.registry_path, "w", encoding="utf-8") as f:
            json.dump(self._registry, f, indent=4)
            
    def register(self, record_data):
        """
        Appends a new execution record to the registry.
        """
        # Ensure minimum required fields exist
        required_fields = [
            "execution_id", "experiment_id", "planner_version",
            "reasoning_version", "knowledge_graph_version",
            "benchmark_version", "dataset_version", "executor_version",
            "execution_timestamp", "execution_directory",
            "execution_status", "artifact_manifest"
        ]
        
        for field in required_fields:
            if field not in record_data:
                raise ValueError(f"[ExecutionRegistry] Missing required field: {field}")
                
        # Check for duplicates
        for r in self._registry["records"]:
            if r["execution_id"] == record_data["execution_id"]:
                return False # Duplicate
                
        self._registry["records"].append(record_data)
        self._registry["total_registered"] = len(self._registry["records"])
        self._registry["last_updated"] = datetime.now().strftime("%Y%m%d_%H%M%S")
        self._save()
        
        return True

    def get_record(self, execution_id):
        for r in self._registry["records"]:
            if r["execution_id"] == execution_id:
                return r
        return None

    @property
    def total_registered(self):
        return self._registry["total_registered"]

    @property
    def version(self):
        return self._registry["registry_version"]
        
    def get_all_records(self):
        return self._registry["records"]
