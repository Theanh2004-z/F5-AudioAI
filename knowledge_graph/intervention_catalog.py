"""
intervention_catalog.py
Static catalog of every intervention point.

Each catalog entry describes an intervention completely:
  - What it is
  - Where it lives in the code
  - What it touches
  - Its structural properties
  - Its evidence basis

This is a read-only catalog.
No optimization logic. No recommendations. No scoring.
"""

from lever_database import LEVER_DATABASE
from feature_graph import FEATURE_GRAPH


def build_intervention_catalog():
    """
    Assembles a complete catalog by joining lever metadata with the feature
    connections from the feature graph.

    Returns:
        dict keyed by lever name, each entry containing:
            - lever metadata (from LEVER_DATABASE)
            - connected_features: list of features this lever can influence
    """
    catalog = {}

    # Reverse the feature graph to get lever → [features]
    lever_to_features = {}
    for feature, lever_entries in FEATURE_GRAPH.items():
        for entry in lever_entries:
            lever_name = entry["lever"]
            if lever_name not in lever_to_features:
                lever_to_features[lever_name] = []
            lever_to_features[lever_name].append({
                "feature":           feature,
                "relationship_type": entry["relationship_type"],
                "evidence":          entry["evidence"]
            })

    for lever_name, lever_meta in LEVER_DATABASE.items():
        catalog[lever_name] = {
            **lever_meta,
            "connected_features": lever_to_features.get(lever_name, [])
        }

    return catalog


# Eagerly built at import time for direct access
INTERVENTION_CATALOG = build_intervention_catalog()
