"""
evaluation_loader.py
Loads evaluation_registry.json.
Selects only PASS and PARTIAL_PASS evaluations.
Skips already-processed evaluations.
Never modifies registry records.
"""

import json
import os
from knowledge_schema import QUALIFYING_DECISIONS

def load_qualifying_evaluations(evaluation_registry_path, knowledge_registry_path):
    """
    Loads evaluation registry and returns records eligible for knowledge building.
    
    Args:
        evaluation_registry_path: Path to evaluation_registry.json
        knowledge_registry_path: Path to knowledge_registry.json
        
    Returns:
        list: Evaluation records qualifying for knowledge extraction.
    """
    if not os.path.exists(evaluation_registry_path):
        print(f"[EvaluationLoader] WARNING: Evaluation registry not found at {evaluation_registry_path}")
        return []

    with open(evaluation_registry_path, "r", encoding="utf-8") as f:
        eval_registry = json.load(f)

    # Load knowledge registry to skip already-processed evaluations
    processed_evaluation_ids = set()
    if os.path.exists(knowledge_registry_path):
        with open(knowledge_registry_path, "r", encoding="utf-8") as f:
            know_registry = json.load(f)
            for r in know_registry.get("records", []):
                processed_evaluation_ids.add(r["evaluation_id"])

    qualifying = []
    for record in eval_registry.get("records", []):
        decision = record.get("decision", "")
        eval_id  = record.get("evaluation_id", "")
        if decision in QUALIFYING_DECISIONS and eval_id not in processed_evaluation_ids:
            qualifying.append(record)

    print(f"[EvaluationLoader] Found {len(qualifying)} qualifying evaluations "
          f"(PASS/PARTIAL_PASS, not yet processed).")
    return qualifying
