"""
learning_statistics.py
"""
import json
import os

def generate_statistics(records, output_dir, metadata_versions):
    total_support = sum(f["support_count"] for r in records for f in r["feature_statistics"].values())
    
    features_hist = {}
    evidence_dist = {"VERY_LOW": 0, "LOW": 0, "MEDIUM": 0, "HIGH": 0, "VERY_HIGH": 0}
    support_dist = {"1_to_5": 0, "6_to_20": 0, "21_to_50": 0, "51_to_100": 0, "100+": 0}
    parameter_dist = {}
    
    for r in records:
        p_name = r["metadata"]["parameter_name"]
        parameter_dist[p_name] = parameter_dist.get(p_name, 0) + 1
        
        for f_name, f_stats in r["feature_statistics"].items():
            features_hist[f_name] = features_hist.get(f_name, 0) + 1
            ev = f_stats["evidence_strength"]
            if ev in evidence_dist:
                evidence_dist[ev] += 1
                
            sup = f_stats["support_count"]
            if sup <= 5: support_dist["1_to_5"] += 1
            elif sup <= 20: support_dist["6_to_20"] += 1
            elif sup <= 50: support_dist["21_to_50"] += 1
            elif sup <= 100: support_dist["51_to_100"] += 1
            else: support_dist["100+"] += 1
            
    stats = {
        "total_learning_records": len(records),
        "total_features": len(features_hist),
        "total_support": total_support,
        "parameter_distribution": parameter_dist,
        "evidence_strength_distribution": evidence_dist,
        "support_distribution": support_dist,
        "dataset_versions": metadata_versions
    }
    
    path = os.path.join(output_dir, "learning_statistics.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=4)
        
    return stats
