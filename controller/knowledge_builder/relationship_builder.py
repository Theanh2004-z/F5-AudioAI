"""
relationship_builder.py
Generates deterministic relationships for the F5-TTS Knowledge Graph.
Only creates relations directly supported by evidence.
No inferred edges, no probabilistic edges.
"""

import os
import sys

# Ensure import access to experiment_evaluator
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "experiment_evaluator")))
from feature_profile_registry import get_feature_profile

RELATIONSHIP_ENGINE_VERSION = "1.0.0"

def build_deterministic_relations(levers_db, registry_records, knowledge_dir):
    """
    Builds nodes and edges from the accumulated levers database and registry records.
    
    Args:
        levers_db (dict): The levers dict from KnowledgeBase.
        registry_records (list): The list of records from KnowledgeRegistry.
        knowledge_dir (str): Path to the knowledge output directory.
        
    Returns:
        dict: A dictionary containing "nodes" and "edges".
    """
    nodes_map = {}
    edges_map = {}

    def add_node(node_id, node_type):
        if not node_id or node_id == "UNKNOWN":
            return
        if node_id not in nodes_map:
            nodes_map[node_id] = {
                "id": node_id,
                "type": node_type
            }

    def add_edge(source, target, rel_type, eval_id, exp_id, know_id):
        if not source or source == "UNKNOWN" or not target or target == "UNKNOWN":
            return
        edge_key = (source, target, rel_type)
        t_ids = {eval_id, exp_id, know_id} - {"UNKNOWN", "", None}
        
        if edge_key not in edges_map:
            edges_map[edge_key] = {
                "source": source,
                "target": target,
                "relationship_type": rel_type,
                "support_count": 0,
                "traceability_ids": set()
            }
        
        edges_map[edge_key]["support_count"] += 1
        edges_map[edge_key]["traceability_ids"].update(t_ids)

    # Process each registered record
    for record in registry_records:
        know_id = record.get("knowledge_id", "UNKNOWN")
        eval_id = record.get("evaluation_id", "UNKNOWN")
        exp_id = record.get("experiment_id", "UNKNOWN")
        lever = record.get("lever", "UNKNOWN")

        # Skip failed/invalid records if any
        if record.get("knowledge_status") == "FAILED" or record.get("decision") not in ["PASS", "PARTIAL_PASS"]:
            continue

        # Register core nodes
        add_node(lever, "LEVER")
        add_node(exp_id, "EXPERIMENT")
        add_node(eval_id, "EVALUATION")
        add_node(know_id, "KNOWLEDGE")

        # Register core edges
        # 1. LEVER_FROM_EXPERIMENT
        add_edge(lever, exp_id, "LEVER_FROM_EXPERIMENT", eval_id, exp_id, know_id)
        # 2. EXPERIMENT_HAS_EVALUATION
        add_edge(exp_id, eval_id, "EXPERIMENT_HAS_EVALUATION", eval_id, exp_id, know_id)
        # 3. EVALUATION_GENERATED_KNOWLEDGE
        add_edge(eval_id, know_id, "EVALUATION_GENERATED_KNOWLEDGE", eval_id, exp_id, know_id)
        # 4. LEVER_SUPPORTED_BY
        add_edge(lever, know_id, "LEVER_SUPPORTED_BY", eval_id, exp_id, know_id)

        # Read the individual knowledge.json to find observed features
        record_dir = record.get("knowledge_directory")
        if not record_dir:
            record_dir = os.path.join(knowledge_dir, know_id)
            
        know_json_path = os.path.join(record_dir, "knowledge.json")
        if os.path.exists(know_json_path):
            import json
            try:
                with open(know_json_path, "r", encoding="utf-8") as f:
                    k_data = json.load(f)
                observed_features = k_data.get("observed_features", [])
                for feat in observed_features:
                    feat_idx = feat.get("feature_index")
                    if feat_idx is not None:
                        feat_prof = get_feature_profile(feat_idx)
                        feat_name = feat_prof.get("feature", f"feature_{feat_idx}")
                        
                        add_node(feat_name, "FEATURE")
                        # 5. LEVER_AFFECTS_FEATURE
                        add_edge(lever, feat_name, "LEVER_AFFECTS_FEATURE", eval_id, exp_id, know_id)
            except Exception as e:
                print(f"[RelationshipBuilder] Warning: Could not read {know_json_path}: {e}")

    # Convert sets to sorted lists for deterministic output
    final_edges = []
    for edge in edges_map.values():
        edge["traceability_ids"] = sorted(list(edge["traceability_ids"]))
        final_edges.append(edge)

    # Sort nodes and edges for determinism
    sorted_nodes = sorted(nodes_map.values(), key=lambda n: (n["type"], n["id"]))
    sorted_edges = sorted(final_edges, key=lambda e: (e["relationship_type"], e["source"], e["target"]))

    return {
        "nodes": sorted_nodes,
        "edges": sorted_edges
    }
