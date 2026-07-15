"""
graph_reasoner.py
Traverses the Knowledge Graph to find candidate levers for each feature.

Given a feature name, returns every lever connected to it via the graph edges,
along with the relationship type and the original evidence string from
the knowledge graph construction phase (Stage 4).

Responsibility: GRAPH TRAVERSAL ONLY.
No hypothesis scoring. No parameter values. No optimization.
"""


def build_feature_lever_index(knowledge_graph):
    """
    Pre-processes the loaded knowledge_graph.json into a fast lookup dict.

    Returns:
        index : dict[feature_name -> list[edge_dict]]
        Each edge_dict contains:
            lever            : str
            relationship_type: str
            evidence         : str
            lever_metadata   : dict (accessibility, coupling, linearity, safety)
    """
    index = {}

    # Build lever metadata lookup from nodes
    lever_meta = {}
    for node in knowledge_graph.get("nodes", []):
        if node.get("node_type") == "LEVER":
            lever_meta[node["id"]] = {
                "accessibility": node.get("accessibility"),
                "coupling":      node.get("coupling"),
                "linearity":     node.get("linearity"),
                "safety":        node.get("safety")
            }

    # Index FEATURE_TO_LEVER edges
    for edge in knowledge_graph.get("edges", []):
        if edge.get("edge_type") != "FEATURE_TO_LEVER":
            continue

        feature = edge["source"]
        lever   = edge["target"]

        if feature not in index:
            index[feature] = []

        index[feature].append({
            "lever":             lever,
            "relationship_type": edge.get("relationship_type", "UNKNOWN"),
            "evidence":          edge.get("evidence", ""),
            "lever_metadata":    lever_meta.get(lever, {})
        })

    return index


def get_candidate_levers(feature_name, feature_lever_index):
    """
    Returns the list of candidate lever edges for a given feature.
    Returns an empty list if the feature has no graph connection.
    """
    return feature_lever_index.get(feature_name, [])
