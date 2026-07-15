"""
knowledge_index.py
Generates knowledge_index.json — fast lookup from lever to IDs.
Rebuilt deterministically from knowledge_base on every run.
"""

import json
import os

KNOWLEDGE_INDEX_VERSION  = "1.0.0"
KNOWLEDGE_INDEX_FILENAME = "knowledge_index.json"

def build_knowledge_index(knowledge_base_levers, base_dir="knowledge"):
    """
    Builds a flat lookup index from the lever map.
    
    Args:
        knowledge_base_levers: dict of levers from KnowledgeBase.get_all_levers()
        base_dir: Output directory.
        
    Returns:
        dict: The index structure.
    """
    index = {
        "knowledge_index_version": KNOWLEDGE_INDEX_VERSION,
        "total_levers": len(knowledge_base_levers),
        "levers":       {}
    }

    for lever, data in knowledge_base_levers.items():
        index["levers"][lever] = {
            "knowledge_ids":   data.get("knowledge_ids", []),
            "experiment_ids":  data.get("supporting_experiments", []),
            "evaluation_ids":  [e["evaluation_id"] for e in data.get("supporting_evaluations", [])],
            "total_observations": data.get("total_observations", 0)
        }

    index_path = os.path.join(base_dir, KNOWLEDGE_INDEX_FILENAME)
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=4)

    return index
