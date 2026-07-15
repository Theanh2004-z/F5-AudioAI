"""
graph_statistics.py
Generates knowledge_graph_statistics.json summarizing graph metrics.
Includes: total_nodes, total_edges, node_histogram, edge_histogram,
largest_connected_component, average_edges_per_node.
"""

import os
import json

GRAPH_STATISTICS_VERSION = "1.0.0"
STATISTICS_FILENAME = "knowledge_graph_statistics.json"

def build_graph_statistics(graph, output_dir):
    """
    Computes graph metrics and saves them to knowledge_graph_statistics.json.
    
    Args:
        graph (dict): The knowledge graph containing "nodes" and "edges".
        output_dir (str): The output directory path.
        
    Returns:
        dict: The computed statistics.
    """
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])

    total_nodes = len(nodes)
    total_edges = len(edges)

    # Node histogram (type -> count)
    node_histogram = {}
    for node in nodes:
        ntype = node.get("type", "UNKNOWN")
        node_histogram[ntype] = node_histogram.get(ntype, 0) + 1

    # Edge histogram (relationship_type -> count)
    edge_histogram = {}
    for edge in edges:
        etype = edge.get("relationship_type", "UNKNOWN")
        edge_histogram[etype] = edge_histogram.get(etype, 0) + 1

    # Largest connected component (undirected graph traversal)
    adj = {node["id"]: set() for node in nodes}
    for edge in edges:
        u = edge["source"]
        v = edge["target"]
        if u in adj and v in adj:
            adj[u].add(v)
            adj[v].add(u)

    visited = set()
    largest_cc_size = 0
    for node_id in adj:
        if node_id not in visited:
            comp_size = 0
            queue = [node_id]
            visited.add(node_id)
            while queue:
                curr = queue.pop(0)
                comp_size += 1
                for neighbor in adj[curr]:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)
            if comp_size > largest_cc_size:
                largest_cc_size = comp_size

    # Average edges per node
    average_edges_per_node = round(total_edges / total_nodes, 4) if total_nodes > 0 else 0.0

    stats = {
        "graph_statistics_version": GRAPH_STATISTICS_VERSION,
        "total_nodes": total_nodes,
        "total_edges": total_edges,
        "node_histogram": node_histogram,
        "edge_histogram": edge_histogram,
        "largest_connected_component": largest_cc_size,
        "average_edges_per_node": average_edges_per_node
    }

    stats_path = os.path.join(output_dir, STATISTICS_FILENAME)
    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=4)

    print(f"[GraphStatistics] Generated statistics at {stats_path}: "
          f"{total_nodes} nodes, {total_edges} edges, LCC={largest_cc_size}.")
    return stats
