"""
analysis_registry.py
Maintains analysis_registry.json. Append-only.
Never overwrites previous records.
"""

import json
import os
from datetime import datetime
from analyzer_schema import ANALYZER_VERSION

REGISTRY_VERSION = "1.0.0"
REGISTRY_FILENAME = "analysis_registry.json"

class AnalysisRegistry:
    def __init__(self, registry_dir="analysis"):
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
        Appends a new analysis record to the registry.
        """
        required_fields = [
            "analysis_id", "benchmark_id", "execution_id", "experiment_id",
            "analysis_timestamp", "analysis_directory", 
            "analysis_status", "analysis_version"
        ]
        
        for field in required_fields:
            if field not in record_data:
                raise ValueError(f"[AnalysisRegistry] Missing required field: {field}")
                
        # Check for duplicates
        for r in self._registry["records"]:
            if r["analysis_id"] == record_data["analysis_id"]:
                return False # Duplicate
                
        self._registry["records"].append(record_data)
        self._registry["total_registered"] = len(self._registry["records"])
        self._registry["last_updated"] = datetime.now().strftime("%Y%m%d_%H%M%S")
        self._save()
        
        return True

    @property
    def total_registered(self):
        return self._registry["total_registered"]

    @property
    def version(self):
        return self._registry["registry_version"]
