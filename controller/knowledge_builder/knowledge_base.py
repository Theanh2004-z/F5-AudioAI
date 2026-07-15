"""
knowledge_base.py
Maintains knowledge/knowledge_base.json.
One record per lever. Deterministic upsert (update or insert).
Never overwrites history — always merges by accumulation.
"""

import json
import os
from datetime import datetime
from knowledge_schema import KNOWLEDGE_BUILDER_VERSION

KNOWLEDGE_BASE_VERSION  = "1.0.0"
KNOWLEDGE_BASE_FILENAME = "knowledge_base.json"

class KnowledgeBase:
    def __init__(self, base_dir="knowledge"):
        self.base_dir   = base_dir
        self.base_path  = os.path.join(base_dir, KNOWLEDGE_BASE_FILENAME)
        os.makedirs(base_dir, exist_ok=True)
        self._db = self._load()

    def _load(self):
        if os.path.exists(self.base_path):
            with open(self.base_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {
            "knowledge_base_version": KNOWLEDGE_BASE_VERSION,
            "created_at":   datetime.now().strftime("%Y%m%d_%H%M%S"),
            "last_updated": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "total_levers": 0,
            "levers":       {}
        }

    def _save(self):
        self._db["last_updated"] = datetime.now().strftime("%Y%m%d_%H%M%S")
        self._db["total_levers"] = len(self._db["levers"])
        with open(self.base_path, "w", encoding="utf-8") as f:
            json.dump(self._db, f, indent=4)

    def upsert_lever(self, lever, aggregation_row, evidence, knowledge_ids):
        """
        Deterministically merges new data into the lever entry.
        Accumulates counts. Never overwrites historical data.
        """
        existing = self._db["levers"].get(lever, {
            "lever":                     lever,
            "total_observations":        0,
            "pass_count":                0,
            "partial_count":             0,
            "fail_count":                0,
            "total_improved_features":   0,
            "total_degraded_features":   0,
            "average_improved_features": 0.0,
            "average_degraded_features": 0.0,
            "supporting_experiments":    [],
            "supporting_evaluations":    [],
            "knowledge_ids":             [],
            "last_updated":              "",
            "knowledge_version":         KNOWLEDGE_BUILDER_VERSION
        })

        # Accumulate counts
        existing["total_observations"]      += aggregation_row.get("total_observations", 0)
        existing["pass_count"]              += aggregation_row.get("pass_count", 0)
        existing["partial_count"]           += aggregation_row.get("partial_pass_count", 0)
        existing["fail_count"]              += aggregation_row.get("fail_count", 0)
        existing["total_improved_features"] += aggregation_row.get("total_improved_features", 0)
        existing["total_degraded_features"] += aggregation_row.get("total_degraded_features", 0)

        # Merge evidence (deduplicate by experiment_id)
        new_exp_ids  = set(evidence.get("supporting_experiments", []))
        new_eval_ids = {e["evaluation_id"] for e in evidence.get("supporting_evaluations", [])}
        existing_exp_set  = set(existing["supporting_experiments"])
        existing_eval_ids = {e["evaluation_id"] for e in existing["supporting_evaluations"]}

        for exp_id in new_exp_ids:
            if exp_id not in existing_exp_set:
                existing["supporting_experiments"].append(exp_id)

        for eval_entry in evidence.get("supporting_evaluations", []):
            if eval_entry["evaluation_id"] not in existing_eval_ids:
                existing["supporting_evaluations"].append(eval_entry)

        for kid in knowledge_ids:
            if kid not in existing["knowledge_ids"]:
                existing["knowledge_ids"].append(kid)

        # Recompute averages
        n = existing["total_observations"]
        if n > 0:
            existing["average_improved_features"] = round(existing["total_improved_features"] / n, 4)
            existing["average_degraded_features"] = round(existing["total_degraded_features"] / n, 4)

        existing["last_updated"]     = datetime.now().strftime("%Y%m%d_%H%M%S")
        existing["knowledge_version"] = KNOWLEDGE_BUILDER_VERSION
        self._db["levers"][lever]    = existing
        self._save()

    def get_all_levers(self):
        return self._db["levers"]

    @property
    def version(self):
        return self._db["knowledge_base_version"]
