"""
graph_validator.py
Validates the structural integrity and constraints of the knowledge graph.
Checks for duplicate nodes, duplicate edges, broken references, missing nodes,
orphan nodes, and invalid edge types.
"""

import os
import json

GRAPH_VALIDATOR_VERSION = "1.0.0"

ALLOWED_RELATIONSHIP_TYPES = {
    "LEVER_AFFECTS_FEATURE",
    "LEVER_SUPPORTED_BY",
    "LEVER_FROM_EXPERIMENT",
    "EXPERIMENT_HAS_EVALUATION",
    "EVALUATION_GENERATED_KNOWLEDGE"
}

ALLOWED_NODE_TYPES = {
    "LEVER",
    "FEATURE",
    "EXPERIMENT",
    "EVALUATION",
    "KNOWLEDGE"
}

def validate_graph(graph):
    """
    Validates a knowledge graph dict.
    
    Args:
        graph (dict): The knowledge graph.
        
    Returns:
        dict: A status dict with "is_valid" (bool) and "errors" (list).
    """
    errors = []
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])

    # 1. Check duplicate nodes & node types
    seen_node_ids = set()
    for node in nodes:
        node_id = node.get("id")
        node_type = node.get("type")
        
        if not node_id:
            errors.append("Node missing 'id'")
            continue
            
        if node_id in seen_node_ids:
            errors.append(f"Duplicate node ID: {node_id}")
        seen_node_ids.add(node_id)
        
        if node_type not in ALLOWED_NODE_TYPES:
            errors.append(f"Node {node_id} has invalid type: {node_type}")

    # 2. Check duplicate edges, edge types, and references
    seen_edges = set()
    node_degrees = {nid: 0 for nid in seen_node_ids}
    
    for idx, edge in enumerate(edges):
        source = edge.get("source")
        target = edge.get("target")
        rel_type = edge.get("relationship_type")
        
        if not source or not target or not rel_type:
            errors.append(f"Edge index {idx} missing 'source', 'target', or 'relationship_type'")
            continue
            
        edge_key = (source, target, rel_type)
        if edge_key in seen_edges:
            errors.append(f"Duplicate edge: {source} -[{rel_type}]-> {target}")
        seen_edges.add(edge_key)
        
        if rel_type not in ALLOWED_RELATIONSHIP_TYPES:
            errors.append(f"Edge index {idx} has invalid relationship_type: {rel_type}")
            
        # Check broken references (missing node declarations)
        if source not in seen_node_ids:
            errors.append(f"Broken reference: Edge source node '{source}' does not exist in nodes list")
        else:
            node_degrees[source] += 1
            
        if target not in seen_node_ids:
            errors.append(f"Broken reference: Edge target node '{target}' does not exist in nodes list")
        else:
            node_degrees[target] += 1

    # 3. Check orphan nodes
    for node_id, degree in node_degrees.items():
        if degree == 0:
            errors.append(f"Orphan node found: '{node_id}' has 0 connections")

    is_valid = len(errors) == 0
    return {
        "is_valid": is_valid,
        "errors": errors
    }

def validate_graph_file(graph_path):
    """Loads and validates a graph file."""
    if not os.path.exists(graph_path):
        return {
            "is_valid": False,
            "errors": [f"Graph file not found: {graph_path}"]
        }
    try:
        with open(graph_path, "r", encoding="utf-8") as f:
            graph = json.load(f)
        return validate_graph(graph)
    except Exception as e:
        return {
            "is_valid": False,
            "errors": [f"Failed to read/parse graph file {graph_path}: {e}"]
        }
