"""
learning_index.py
"""
import json
import os

def generate_index(records, output_dir):
    index = {}
    for r in records:
        lever = r["metadata"]["lever"]
        p_name = r["metadata"]["parameter_name"]
        p_val = str(r["metadata"]["parameter_value"])
        r_id = r["learning_record_id"]
        
        if lever not in index: index[lever] = {}
        if p_name not in index[lever]: index[lever][p_name] = {}
        if p_val not in index[lever][p_name]: index[lever][p_name][p_val] = {}
        
        for f_name, f_stats in r["feature_statistics"].items():
            index[lever][p_name][p_val][f_name] = {
                "learning_record_id": r_id,
                "support_count": f_stats["support_count"],
                "evidence_strength": f_stats["evidence_strength"]
            }
            
    path = os.path.join(output_dir, "learning_index.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=4)
        
    return index
