"""
graph_index.py
Generates knowledge_graph_index.json for fast lookup of connected nodes by lever.
"""

import os
import json

GRAPH_INDEX_VERSION = "1.0.0"
INDEX_FILENAME = "knowledge_graph_index.json"

def build_graph_index(graph, output_dir):
    """
    Builds a fast lookup index from the knowledge graph.
    Saves to knowledge_graph_index.json.
    
    Args:
        graph (dict): The knowledge graph dictionary containing "nodes" and "edges".
        output_dir (str): The output directory path.
        
    Returns:
        dict: The index dictionary.
    """
    index = {
        "graph_index_version": GRAPH_INDEX_VERSION,
        "levers": {}
    }

    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])

    # Find all lever node IDs
    lever_ids = [node["id"] for node in nodes if node["type"] == "LEVER"]

    for lever in lever_ids:
        # 1. Connected features (LEVER_AFFECTS_FEATURE target)
        features = sorted(list({
            edge["target"] for edge in edges 
            if edge["source"] == lever and edge["relationship_type"] == "LEVER_AFFECTS_FEATURE"
        }))

        # 2. Connected experiments (LEVER_FROM_EXPERIMENT target)
        experiments = sorted(list({
            edge["target"] for edge in edges 
            if edge["source"] == lever and edge["relationship_type"] == "LEVER_FROM_EXPERIMENT"
        }))

        # 3. Connected evaluations (EXPERIMENT_HAS_EVALUATION target for lever's experiments)
        evaluations = sorted(list({
            edge["target"] for edge in edges 
            if edge["source"] in experiments and edge["relationship_type"] == "EXPERIMENT_HAS_EVALUATION"
        }))

        # 4. Connected knowledge ids (LEVER_SUPPORTED_BY target)
        knowledge_ids = sorted(list({
            edge["target"] for edge in edges 
            if edge["source"] == lever and edge["relationship_type"] == "LEVER_SUPPORTED_BY"
        }))

        index["levers"][lever] = {
            "features": features,
            "experiments": experiments,
            "evaluations": evaluations,
            "knowledge_ids": knowledge_ids
        }

    index_path = os.path.join(output_dir, INDEX_FILENAME)
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=4)

    print(f"[GraphIndex] Generated index at {index_path} with {len(index['levers'])} levers.")
    return index
