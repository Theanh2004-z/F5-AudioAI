"""
knowledge_graph.py
Orchestrates F5-TTS Knowledge Graph generation and saves knowledge_graph.json.
Node Types: LEVER, FEATURE, EXPERIMENT, EVALUATION, KNOWLEDGE
Edges: LEVER_AFFECTS_FEATURE, LEVER_SUPPORTED_BY, LEVER_FROM_EXPERIMENT, EXPERIMENT_HAS_EVALUATION, EVALUATION_GENERATED_KNOWLEDGE
"""

import os
import json
from relationship_builder import build_deterministic_relations

KNOWLEDGE_GRAPH_VERSION = "1.0.0"
GRAPH_FILENAME = "knowledge_graph.json"

def build_knowledge_graph(levers_db, registry, output_dir):
    """
    Builds the knowledge graph from KnowledgeBase and KnowledgeRegistry.
    Saves the output to knowledge_graph.json.
    
    Args:
        levers_db (dict): The levers dictionary from KnowledgeBase.
        registry (KnowledgeRegistry): The KnowledgeRegistry instance.
        output_dir (str): The directory where knowledge_graph.json will be saved.
        
    Returns:
        dict: The generated graph.
    """
    records = registry._registry.get("records", [])
    graph = build_deterministic_relations(levers_db, records, output_dir)
    
    # Add graph version to the output structure
    graph["knowledge_graph_version"] = KNOWLEDGE_GRAPH_VERSION
    
    graph_path = os.path.join(output_dir, GRAPH_FILENAME)
    with open(graph_path, "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=4)
        
    print(f"[KnowledgeGraph] Generated graph at {graph_path} with {len(graph['nodes'])} nodes and {len(graph['edges'])} edges.")
    return graph
