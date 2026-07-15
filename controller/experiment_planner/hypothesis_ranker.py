"""
hypothesis_ranker.py
Ranks lever hypotheses from the reasoning_report by reasoning_confidence.
Filters out hypotheses below the configurable threshold and those
targeting blocked (unsafe) levers.

No optimization. No parameter recommendation. Pure ranking and filtering.
"""

from planner_config import (
    MIN_CONFIDENCE_THRESHOLD,
    BLOCKED_SAFETY_CLASSES,
    MAX_ACCEPTABLE_CONFLICT_COUNT
)


def rank_hypotheses(lever_hypotheses, parameter_registry):
    """
    Filters and ranks lever hypotheses for experiment planning.

    Args:
        lever_hypotheses   : list[dict] — from reasoning_report["lever_hypotheses"]
        parameter_registry : list[dict] — loaded from parameter_registry.json

    Returns:
        ranked     : list[dict]  — filtered and sorted lever hypotheses
        skipped    : list[dict]  — hypotheses that were filtered out, with reason
        rank_warnings : list[str]
    """
    # Build quick lookup: lever_name → registry entry
    reg_lookup = {r["name"]: r for r in parameter_registry}

    ranked        = []
    skipped       = []
    rank_warnings = []

    for lh in lever_hypotheses:
        lever  = lh["lever"]
        conf   = lh.get("reasoning_confidence", 0.0)
        n_conf = lh.get("conflict_count", 0)

        # 1. Skip levers not in parameter_registry (not API-accessible)
        if lever not in reg_lookup:
            skipped.append({
                "lever":  lever,
                "reason": "Lever not found in parameter_registry. "
                          "May be INTERNAL_ONLY or not yet registered."
            })
            continue

        reg = reg_lookup[lever]

        # 2. Safety gate — never plan for EXTREME_RISK levers
        safety = reg.get("safety", "UNKNOWN")
        if safety in BLOCKED_SAFETY_CLASSES:
            skipped.append({
                "lever":  lever,
                "reason": f"Safety class '{safety}' is blocked. "
                          f"This lever must not appear in any experiment plan."
            })
            continue

        # 3. Confidence threshold
        if conf < MIN_CONFIDENCE_THRESHOLD:
            skipped.append({
                "lever":  lever,
                "reason": f"reasoning_confidence={conf:.4f} below "
                          f"MIN_CONFIDENCE_THRESHOLD={MIN_CONFIDENCE_THRESHOLD}."
            })
            continue

        # 4. Conflict warning (does not block, only warns)
        if n_conf > MAX_ACCEPTABLE_CONFLICT_COUNT:
            rank_warnings.append(
                f"[{lever}] conflict_count={n_conf} exceeds "
                f"MAX_ACCEPTABLE_CONFLICT_COUNT={MAX_ACCEPTABLE_CONFLICT_COUNT}. "
                f"Plan included but interpret results carefully."
            )

        ranked.append({**lh, "_registry": reg})

    # Sort by descending reasoning_confidence
    ranked.sort(key=lambda x: x["reasoning_confidence"], reverse=True)

    return ranked, skipped, rank_warnings
