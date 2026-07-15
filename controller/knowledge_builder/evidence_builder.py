"""
evidence_builder.py
Builds knowledge_evidence.json per lever.
Aggregates supporting/partial evaluations. No causal inference. Pure statistics.
"""

def build_evidence(lever, aggregation_row, all_knowledge_records):
    """
    Builds evidence record for a specific lever.
    
    Args:
        lever: The lever name string.
        aggregation_row: Aggregated stats from knowledge_aggregator.
        all_knowledge_records: All knowledge records from this build run.
        
    Returns:
        dict: Evidence structure for this lever.
    """
    supporting_experiments  = []
    supporting_evaluations  = []

    for record in all_knowledge_records:
        if record.get("lever") != lever:
            continue

        decision = record.get("decision", "")
        entry = {
            "evaluation_id":  record.get("evaluation_id"),
            "experiment_id":  record.get("experiment_id"),
            "decision":       decision
        }

        if decision == "PASS":
            supporting_experiments.append(record.get("experiment_id"))
            supporting_evaluations.append(entry)
        elif decision == "PARTIAL_PASS":
            supporting_evaluations.append(entry)

    return {
        "lever":                   lever,
        "supporting_experiments":  list(set(supporting_experiments)),  # deduplicate experiment IDs
        "supporting_evaluations":  supporting_evaluations,
        "support_count":           aggregation_row.get("pass_count", 0),
        "partial_count":           aggregation_row.get("partial_pass_count", 0),
        "total_observations":      aggregation_row.get("total_observations", 0),
        "average_improved_features": aggregation_row.get("average_improved_features", 0.0),
        "average_degraded_features": aggregation_row.get("average_degraded_features", 0.0)
    }
