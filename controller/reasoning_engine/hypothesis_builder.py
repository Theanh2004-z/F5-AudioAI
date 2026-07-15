"""
hypothesis_builder.py
Constructs hypothesis objects by joining evidence packets with
knowledge graph edges.

A hypothesis answers:
  "Given this observation, which lever is a candidate cause?"

A hypothesis does NOT answer:
  "What value should I set the lever to?"

Responsibility: HYPOTHESIS CONSTRUCTION ONLY.
No parameter values. No tuning. No optimization.
"""

from graph_reasoner import get_candidate_levers
from confidence_fusion import fuse_confidence
from reasoning_schema import WEAK_HYPOTHESIS_THRESHOLD


def _build_supporting_evidence(evidence_packet, edge):
    """
    Assembles a list of human-readable evidence strings from all sources.
    These are purely descriptive statements about what was observed and
    what the knowledge graph states — NOT recommendations.
    """
    ev = []

    # From Knowledge Graph
    ev.append(
        f"[Knowledge Graph] Feature '{evidence_packet['feature']}' → lever '{edge['lever']}' "
        f"via {edge['relationship_type']} edge. "
        f"Graph evidence: \"{edge['evidence']}\""
    )

    # From Observation Report
    ev.append(
        f"[Observation] Generated quality: {evidence_packet['gen_quality']} | "
        f"Reference quality: {evidence_packet['ref_quality']}"
    )

    # From Confidence Report
    ev.append(
        f"[Confidence] ref={evidence_packet['ref_confidence']:.4f}, "
        f"gen={evidence_packet['gen_confidence']:.4f}"
    )

    # From Normalized Difference
    nd = evidence_packet.get("normalized_difference")
    if nd is not None:
        direction = "above reference" if nd > 0 else "below reference"
        ev.append(
            f"[Normalized Difference] {nd:+.4f} ({direction}) "
            f"| observation_strength={evidence_packet['observation_strength']:.4f}"
        )

    # From Lever Metadata
    meta = edge.get("lever_metadata", {})
    if meta:
        ev.append(
            f"[Lever Properties] accessibility={meta.get('accessibility','?')}, "
            f"coupling={meta.get('coupling','?')}, "
            f"linearity={meta.get('linearity','?')}, "
            f"safety={meta.get('safety','?')}"
        )

    return ev


def build_hypotheses(evidence_map, feature_lever_index):
    """
    Produces candidate hypotheses and unknowns for all features
    in the evidence map.

    Args:
        evidence_map        : dict[feature -> evidence_packet] from evidence_collector
        feature_lever_index : dict from graph_reasoner.build_feature_lever_index

    Returns:
        feature_observations : list[dict]  — summary of each feature observation
        hypotheses           : list[dict]  — candidate hypothesis objects
        unknowns             : list[dict]  — features with observation but no graph path
        warnings             : list[str]
    """
    feature_observations = []
    hypotheses           = []
    unknowns             = []
    warnings             = []

    for feature, ep in evidence_map.items():
        # ── Feature observation summary ────────────────────────────────────
        feature_observations.append({
            "feature":               feature,
            "normalized_difference": ep["normalized_difference"],
            "observation_quality":   ep["gen_quality"],
            "ref_confidence":        ep["ref_confidence"],
            "gen_confidence":        ep["gen_confidence"],
            "observation_strength":  ep["observation_strength"]
        })

        # Skip features with zero observation strength (nothing notable to reason about)
        if ep["observation_strength"] == 0.0:
            continue

        # ── Graph lookup ───────────────────────────────────────────────────
        edges = get_candidate_levers(feature, feature_lever_index)

        if not edges:
            unknowns.append({
                "feature": feature,
                "reason":  "No edge found in knowledge graph for this feature. "
                           "Cannot identify a candidate lever."
            })
            continue

        # ── Build one hypothesis per graph edge ────────────────────────────
        for edge in edges:
            reasoning_confidence = fuse_confidence(
                gen_quality          = ep["gen_quality"],
                ref_confidence       = ep["ref_confidence"],
                gen_confidence       = ep["gen_confidence"],
                relationship_type    = edge["relationship_type"],
                observation_strength = ep["observation_strength"]
            )

            supporting_evidence = _build_supporting_evidence(ep, edge)

            hypothesis = {
                "feature":              feature,
                "candidate_lever":      edge["lever"],
                "relationship_type":    edge["relationship_type"],
                "supporting_evidence":  supporting_evidence,
                "reasoning_confidence": reasoning_confidence
            }

            if reasoning_confidence < WEAK_HYPOTHESIS_THRESHOLD:
                warnings.append(
                    f"[WEAK] Hypothesis ({feature} → {edge['lever']}) has low "
                    f"reasoning_confidence={reasoning_confidence:.4f}. "
                    f"Observation may be unreliable."
                )

            hypotheses.append(hypothesis)

    # Sort hypotheses by descending reasoning_confidence for readability
    hypotheses.sort(key=lambda h: h["reasoning_confidence"], reverse=True)

    return feature_observations, hypotheses, unknowns, warnings
