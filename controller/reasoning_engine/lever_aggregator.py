"""
lever_aggregator.py
Groups all feature-level hypotheses by lever, producing one final
lever hypothesis per unique lever.

Responsibilities:
  - Group all hypotheses belonging to the same lever
  - Count supporting features (observation_strength > 0, non-conflicting)
  - Count conflicting features (opposite normalized_difference directions
    across DIRECT edges to the same lever)
  - Calculate evidence coverage
  - Merge all supporting evidence strings
  - Produce one final aggregated hypothesis per lever

Contradiction definition:
  Two features are in conflict for the same lever when:
    - Both have relationship_type == DIRECT to that lever
    - Their normalized_difference values have opposite signs (+/-)
    - Both have observation_strength > 0
  This means the two observations cannot be simultaneously explained
  by a single monotonic change in that lever.

Do NOT resolve conflicts. Only detect and report them.
No optimization. No parameter values. No tuning.
"""

import math


def _opposite_signs(a, b):
    """True if a and b are non-zero and have opposite signs."""
    if a is None or b is None:
        return False
    if a == 0.0 or b == 0.0:
        return False
    return (a > 0) != (b > 0)


def aggregate_by_lever(feature_hypotheses, evidence_map):
    """
    Aggregates feature-level hypotheses into lever-centric hypothesis objects.

    Args:
        feature_hypotheses : list[dict]  — from hypothesis_builder.build_hypotheses
        evidence_map       : dict        — from evidence_collector.collect_evidence

    Returns:
        lever_hypotheses : list[dict]  — one entry per unique lever
        agg_warnings     : list[str]
    """
    agg_warnings = []

    # ── Step 1: Group hypotheses by lever ─────────────────────────────────
    lever_groups = {}   # lever_name → list of hypothesis dicts
    for h in feature_hypotheses:
        lever = h["candidate_lever"]
        lever_groups.setdefault(lever, []).append(h)

    lever_hypotheses = []

    for lever, hyps in lever_groups.items():

        # ── Step 2: Collect feature metadata for this lever ───────────────
        features_info = []
        for h in hyps:
            ep = evidence_map.get(h["feature"], {})
            features_info.append({
                "feature":               h["feature"],
                "relationship_type":     h["relationship_type"],
                "normalized_difference": ep.get("normalized_difference"),
                "observation_strength":  ep.get("observation_strength", 0.0),
                "gen_quality":           ep.get("gen_quality", "MISSING"),
                "reasoning_confidence":  h["reasoning_confidence"]
            })

        # ── Step 3: Contradiction detection ───────────────────────────────
        # Only check DIRECT relationships for true contradictions
        direct_features = [f for f in features_info if f["relationship_type"] == "DIRECT"
                           and f["observation_strength"] > 0.0]

        supporting_features  = []
        conflicting_features = []
        conflict_pairs       = []

        if len(direct_features) > 1:
            # Pairwise check for sign conflicts
            checked = set()
            for i, fa in enumerate(direct_features):
                for j, fb in enumerate(direct_features):
                    if j <= i:
                        continue
                    pair_key = (fa["feature"], fb["feature"])
                    if pair_key in checked:
                        continue
                    checked.add(pair_key)
                    if _opposite_signs(fa["normalized_difference"], fb["normalized_difference"]):
                        conflict_pairs.append(pair_key)
                        if fa["feature"] not in conflicting_features:
                            conflicting_features.append(fa["feature"])
                        if fb["feature"] not in conflicting_features:
                            conflicting_features.append(fb["feature"])

                        agg_warnings.append(
                            f"[CONFLICT] Lever '{lever}': features "
                            f"'{fa['feature']}' (diff={fa['normalized_difference']:+.4f}) "
                            f"and '{fb['feature']}' (diff={fb['normalized_difference']:+.4f}) "
                            f"produce contradictory observations on a DIRECT edge."
                        )

        # Non-conflicting features are supporting
        conflict_set = set(conflicting_features)
        for fi in features_info:
            fname = fi["feature"]
            if fname not in conflict_set and fi["observation_strength"] > 0.0:
                supporting_features.append(fname)

        # Unknown: features with zero observation_strength (nothing notable to observe)
        unknown_features = [fi["feature"] for fi in features_info
                            if fi["observation_strength"] == 0.0]

        support_count  = len(supporting_features)
        conflict_count = len(conflicting_features)
        unknown_count  = len(unknown_features)
        total          = len(features_info)

        # ── Step 4: Evidence statistics ───────────────────────────────────
        all_evidence = []
        for h in hyps:
            all_evidence.extend(h.get("supporting_evidence", []))

        evidence_count = len(all_evidence)

        # coverage = fraction of features that clearly support (not conflict, not unknown)
        coverage = round(support_count / total, 4) if total > 0 else 0.0

        # ── Step 5: Lever reasoning_confidence ───────────────────────────
        # Weighted average of supporting hypothesis confidences,
        # penalised by a conflict fraction.
        # This is purely descriptive — NOT a tuning signal.
        if supporting_features:
            supporting_confs = [fi["reasoning_confidence"] for fi in features_info
                                if fi["feature"] in supporting_features]
            base_conf = sum(supporting_confs) / len(supporting_confs)
        else:
            base_conf = 0.0

        conflict_penalty = conflict_count / total if total > 0 else 0.0
        lever_conf = round(max(0.0, base_conf * (1.0 - conflict_penalty)), 4)

        # ── Step 6: Assemble lever hypothesis ────────────────────────────
        lever_hypotheses.append({
            "lever":               lever,
            "supporting_features": supporting_features,
            "conflicting_features": conflicting_features,
            "unknown_features":    unknown_features,
            "support_count":       support_count,
            "conflict_count":      conflict_count,
            "unknown_count":       unknown_count,
            "coverage":            coverage,
            "reasoning_confidence": lever_conf,
            "conflict_pairs":      [list(p) for p in conflict_pairs],
            "evidence_statistics": {
                "evidence_count": evidence_count,
                "support_count":  support_count,
                "conflict_count": conflict_count,
                "unknown_count":  unknown_count,
                "coverage":       coverage
            },
            "evidence": all_evidence
        })

    # Sort by descending reasoning_confidence
    lever_hypotheses.sort(key=lambda x: x["reasoning_confidence"], reverse=True)

    return lever_hypotheses, agg_warnings
