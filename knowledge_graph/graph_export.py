"""
graph_export.py
Serializes the complete Knowledge Graph to JSON.

Exports:
  - knowledge_graph.json : Full graph with nodes (levers, features) and edges
  - graph_index.json     : Lightweight lookup index for quick traversal

No optimization. No parameter recommendation. Pure serialization.
"""

import json
import os
from datetime import datetime

from lever_database import LEVER_DATABASE
from feature_graph import FEATURE_GRAPH
from dependency_graph import DEPENDENCY_GRAPH
from intervention_catalog import INTERVENTION_CATALOG


KNOWLEDGE_GRAPH_VERSION = "1.0.0"


def _build_nodes():
    """
    Builds the node list for the graph.
    Two node types: 'FEATURE' and 'LEVER'.
    """
    nodes = []

    # Feature nodes — one per entry in FEATURE_GRAPH
    for feature_name in FEATURE_GRAPH:
        nodes.append({
            "id":        feature_name,
            "node_type": "FEATURE",
            "group":     _infer_feature_group(feature_name)
        })

    # Lever nodes — one per entry in LEVER_DATABASE
    for lever_name, meta in LEVER_DATABASE.items():
        nodes.append({
            "id":            lever_name,
            "node_type":     "LEVER",
            "lever_id":      meta["lever_id"],
            "accessibility": meta["accessibility"],
            "safety":        meta["safety"],
            "coupling":      meta["coupling"],
            "linearity":     meta["linearity"]
        })

    return nodes


def _infer_feature_group(feature_name):
    """Simple prefix-based group inference."""
    if feature_name.startswith("pitch"):     return "Pitch"
    if feature_name.startswith("energy"):    return "Energy"
    if feature_name.startswith("rhythm"):    return "Rhythm"
    if feature_name.startswith("spectral"):  return "Spectral"
    if feature_name.startswith("vq"):        return "Voice Quality"
    return "Unknown"


def _build_edges():
    """
    Builds the edge list for the graph.
    Two edge types:
      'FEATURE_TO_LEVER'  : feature -> lever (from feature_graph)
      'LEVER_DEPENDENCY'  : lever -> lever (from dependency_graph)
    """
    edges = []

    for feature, lever_entries in FEATURE_GRAPH.items():
        for entry in lever_entries:
            edges.append({
                "edge_type":         "FEATURE_TO_LEVER",
                "source":            feature,
                "target":            entry["lever"],
                "relationship_type": entry["relationship_type"],
                "evidence":          entry["evidence"]
            })

    for lever, deps in DEPENDENCY_GRAPH.items():
        for dep in deps:
            edges.append({
                "edge_type":   "LEVER_DEPENDENCY",
                "source":      lever,
                "target":      dep["depends_on"],
                "relationship": dep["relationship"],
                "direction":   dep["direction"],
                "description": dep["description"]
            })

    return edges


def export_knowledge_graph(output_dir="."):
    """
    Serializes nodes + edges to knowledge_graph.json.
    Serializes the index lookup to graph_index.json.
    """
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    nodes = _build_nodes()
    edges = _build_edges()

    # ── knowledge_graph.json ──────────────────────────────────────────────
    knowledge_graph = {
        "metadata": {
            "version":   KNOWLEDGE_GRAPH_VERSION,
            "timestamp": timestamp,
            "description": (
                "Static knowledge graph connecting acoustic features to F5-TTS "
                "inference levers. Describes relationships only — no optimization."
            ),
            "node_count": len(nodes),
            "edge_count":  len(edges)
        },
        "nodes": nodes,
        "edges": edges,
        "intervention_catalog": INTERVENTION_CATALOG
    }

    kg_path = os.path.join(output_dir, "knowledge_graph.json")
    with open(kg_path, "w", encoding="utf-8") as f:
        json.dump(knowledge_graph, f, indent=4)

    # ── graph_index.json ─────────────────────────────────────────────────
    # Lightweight index: feature → [lever names]  and  lever → [feature names]
    feature_to_levers = {}
    lever_to_features = {}

    for edge in edges:
        if edge["edge_type"] == "FEATURE_TO_LEVER":
            src, tgt = edge["source"], edge["target"]
            feature_to_levers.setdefault(src, [])
            if tgt not in feature_to_levers[src]:
                feature_to_levers[src].append(tgt)
            lever_to_features.setdefault(tgt, [])
            if src not in lever_to_features[tgt]:
                lever_to_features[tgt].append(src)

    graph_index = {
        "metadata": {
            "version":   KNOWLEDGE_GRAPH_VERSION,
            "timestamp": timestamp
        },
        "feature_to_levers": feature_to_levers,
        "lever_to_features": lever_to_features,
        "lever_accessibility": {
            name: meta["accessibility"]
            for name, meta in LEVER_DATABASE.items()
        },
        "lever_dependencies": {
            lever: [d["depends_on"] for d in deps]
            for lever, deps in DEPENDENCY_GRAPH.items()
        }
    }

    idx_path = os.path.join(output_dir, "graph_index.json")
    with open(idx_path, "w", encoding="utf-8") as f:
        json.dump(graph_index, f, indent=4)

    print(f"✅ knowledge_graph.json  → {kg_path}")
    print(f"✅ graph_index.json      → {idx_path}")
    return kg_path, idx_path


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Export F5-TTS Knowledge Graph")
    parser.add_argument("--output_dir", type=str, default=".", help="Output directory")
    args = parser.parse_args()
    export_knowledge_graph(args.output_dir)
