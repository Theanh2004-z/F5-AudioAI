"""
knowledge_statistics.py
Generates knowledge_global_statistics.json from the global knowledge base.
No ranking algorithm. Pure counting and ratio computation.
"""

import json
import os

KNOWLEDGE_STATISTICS_VERSION  = "1.0.0"
KNOWLEDGE_STATISTICS_FILENAME = "knowledge_global_statistics.json"

def build_knowledge_statistics(knowledge_base_levers, base_dir="knowledge"):
    """
    Computes global statistics over all levers in the knowledge base.
    
    Args:
        knowledge_base_levers: dict of levers from KnowledgeBase.get_all_levers()
        base_dir: Output directory.
        
    Returns:
        dict: Global statistics.
    """
    total_levers  = len(knowledge_base_levers)
    total_records = 0
    total_support = 0
    total_partial = 0
    total_fail    = 0

    lever_support_counts  = {}  # lever -> pass_count (for top_supported lookup)
    lever_obs_counts      = {}  # lever -> total_observations

    for lever, data in knowledge_base_levers.items():
        obs = data.get("total_observations", 0)
        sup = data.get("pass_count", 0)
        par = data.get("partial_count", 0)
        fai = data.get("fail_count", 0)

        total_records += obs
        total_support += sup
        total_partial += par
        total_fail    += fai

        lever_support_counts[lever] = sup
        lever_obs_counts[lever]     = obs

    total_decisions = total_records
    pass_ratio      = round(total_support / total_decisions, 4) if total_decisions > 0 else 0.0
    partial_ratio   = round(total_partial / total_decisions, 4) if total_decisions > 0 else 0.0
    avg_support     = round(total_support / total_levers, 4) if total_levers > 0 else 0.0

    # Largest evidence group = lever with most total_observations
    largest_evidence_group = max(lever_obs_counts, key=lever_obs_counts.get) if lever_obs_counts else None

    # Top supported levers = sorted by pass_count descending (counting only, not ranking by score)
    top_supported_levers = sorted(lever_support_counts, key=lever_support_counts.get, reverse=True)

    stats = {
        "knowledge_statistics_version": KNOWLEDGE_STATISTICS_VERSION,
        "total_levers":               total_levers,
        "total_records":              total_records,
        "total_support":              total_support,
        "total_partial":              total_partial,
        "total_fail":                 total_fail,
        "pass_ratio":                 pass_ratio,
        "partial_ratio":              partial_ratio,
        "average_support_per_lever":  avg_support,
        "largest_evidence_group":     largest_evidence_group,
        "top_supported_levers":       top_supported_levers
    }

    stats_path = os.path.join(base_dir, KNOWLEDGE_STATISTICS_FILENAME)
    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=4)

    return stats
