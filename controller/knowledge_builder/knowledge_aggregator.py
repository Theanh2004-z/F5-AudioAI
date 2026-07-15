"""
knowledge_aggregator.py
Aggregates knowledge records by lever.
No scoring, no ranking, no optimization. Deterministic counting only.
"""

from collections import defaultdict

def aggregate_by_lever(all_knowledge_records):
    """
    Groups knowledge records by lever and computes deterministic statistics.
    
    Args:
        all_knowledge_records: List of knowledge dicts from knowledge_extractor.
        
    Returns:
        dict: Lever-keyed aggregation.
    """
    lever_map = defaultdict(lambda: {
        "lever": "",
        "total_observations": 0,
        "pass_count": 0,
        "partial_pass_count": 0,
        "fail_count": 0,
        "total_improved_features": 0,
        "total_degraded_features": 0,
        "total_unchanged_features": 0,
        "average_improved_features": 0.0,
        "average_degraded_features": 0.0,
        "evaluation_ids": []
    })

    for record in all_knowledge_records:
        lever    = record.get("lever", "UNKNOWN")
        decision = record.get("decision", "UNKNOWN")
        features = record.get("observed_features", [])
        eval_id  = record.get("evaluation_id", "")

        agg = lever_map[lever]
        agg["lever"] = lever
        agg["total_observations"] += 1
        agg["evaluation_ids"].append(eval_id)

        if decision == "PASS":
            agg["pass_count"] += 1
        elif decision == "PARTIAL_PASS":
            agg["partial_pass_count"] += 1
        else:
            agg["fail_count"] += 1

        for feat in features:
            outcome = feat.get("outcome", "")
            if outcome == "IMPROVED":
                agg["total_improved_features"] += 1
            elif outcome == "DEGRADED":
                agg["total_degraded_features"] += 1
            elif outcome == "UNCHANGED":
                agg["total_unchanged_features"] += 1

    # Compute averages per lever
    for lever, agg in lever_map.items():
        n = agg["total_observations"]
        if n > 0:
            agg["average_improved_features"] = round(agg["total_improved_features"] / n, 4)
            agg["average_degraded_features"] = round(agg["total_degraded_features"] / n, 4)

    return dict(lever_map)
