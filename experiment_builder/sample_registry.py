"""
sample_registry.py
Maintains a running index of every recorded experiment.

The registry is the single source of truth for experiment discovery.
It persists as sample_registry.json in the dataset/ directory.

No AI. No optimization. No recommendation.
Pure index management.
"""

import json
import os
from datetime import datetime

REGISTRY_FILENAME = "sample_registry.json"
DATASET_VERSION   = "1.0.0"


class SampleRegistry:
    def __init__(self, dataset_dir="dataset"):
        self.dataset_dir    = dataset_dir
        self.registry_path  = os.path.join(dataset_dir, REGISTRY_FILENAME)
        os.makedirs(dataset_dir, exist_ok=True)
        self._registry = self._load()

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _load(self):
        if os.path.exists(self.registry_path):
            with open(self.registry_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {
            "dataset_version": DATASET_VERSION,
            "created_at":      datetime.now().strftime("%Y%m%d_%H%M%S"),
            "total_samples":   0,
            "samples":         []
        }

    def _save(self):
        with open(self.registry_path, "w", encoding="utf-8") as f:
            json.dump(self._registry, f, indent=4)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def next_experiment_id(self):
        """Returns the next zero-padded experiment ID string."""
        return f"experiment_{(self._registry['total_samples'] + 1):06d}"

    def register(self, experiment_id, experiment_dir, metadata):
        """
        Appends one experiment entry to the registry.
        metadata: dict with at minimum { timestamp, ref_audio, gen_audio }
        """
        entry = {
            "experiment_id":    experiment_id,
            "experiment_dir":   experiment_dir,
            "registered_at":    datetime.now().strftime("%Y%m%d_%H%M%S"),
            **metadata
        }
        self._registry["samples"].append(entry)
        self._registry["total_samples"] = len(self._registry["samples"])
        self._registry["last_updated"]  = datetime.now().strftime("%Y%m%d_%H%M%S")
        self._save()
        return entry

    def get_all(self):
        return self._registry["samples"]

    def get_by_id(self, experiment_id):
        for s in self._registry["samples"]:
            if s["experiment_id"] == experiment_id:
                return s
        return None

    @property
    def total_samples(self):
        return self._registry["total_samples"]

    @property
    def dataset_version(self):
        return self._registry["dataset_version"]
