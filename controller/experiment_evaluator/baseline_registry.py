"""
baseline_registry.py
Manages baseline definitions for evaluation comparisons.
Baseline records are static and append-only.
"""

import os
import json
from datetime import datetime

BASELINE_VERSION = "1.0.0"
BASELINE_REGISTRY_FILENAME = "baseline_registry.json"

# Default in-built baseline used when no external baseline is registered
DEFAULT_BASELINE = {
    "baseline_id": "BASELINE-default",
    "baseline_version": BASELINE_VERSION,
    "baseline_name": "zero_vector_baseline",
    "description": "Reference baseline is the zero-delta vector (generated == reference).",
    "baseline_created_at": "2026-07-01T00:00:00Z",
    "type": "BUILT_IN"
}

class BaselineRegistry:
    def __init__(self, registry_dir="evaluation"):
        self.registry_dir = registry_dir
        self.registry_path = os.path.join(registry_dir, BASELINE_REGISTRY_FILENAME)
        os.makedirs(registry_dir, exist_ok=True)
        self._registry = self._load()

    def _load(self):
        if os.path.exists(self.registry_path):
            with open(self.registry_path, "r", encoding="utf-8") as f:
                return json.load(f)
        # Seed with the default baseline and persist immediately
        seed = {
            "registry_version": "1.0.0",
            "created_at": datetime.now().strftime("%Y%m%dT%H%M%SZ"),
            "baselines": [DEFAULT_BASELINE]
        }
        with open(self.registry_path, "w", encoding="utf-8") as f:
            json.dump(seed, f, indent=4)
        return seed

    def _save(self):
        with open(self.registry_path, "w", encoding="utf-8") as f:
            json.dump(self._registry, f, indent=4)

    def get_active_baseline(self):
        """Returns the most recently added baseline as active."""
        baselines = self._registry.get("baselines", [DEFAULT_BASELINE])
        return baselines[-1] if baselines else DEFAULT_BASELINE

    def register_baseline(self, baseline_data):
        """Appends a new baseline record. Append-only."""
        self._registry["baselines"].append(baseline_data)
        self._save()
        return True
