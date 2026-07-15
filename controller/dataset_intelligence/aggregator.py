"""
aggregator.py
"""
import math
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from learning_rule_registry import get_bin, HISTOGRAM_BINS

def aggregate_samples(samples):
    groups = {}
    
    for sample in samples:
        lever = sample.get("lever", "")
        p_vals = sample.get("parameter_values", {})
        if not p_vals:
            p_vals = {"unknown_param": 0}
            
        decision = sample.get("decision", "FAIL")
        feature_deltas = sample.get("feature_deltas", {})
        
        s_id = sample.get("sample_id", "")
        k_id = sample.get("knowledge_id", "")
        e_id = sample.get("evaluation_id", "")
        x_id = sample.get("experiment_id", "")
        
        for p_name, p_val in p_vals.items():
            for f_name, f_val in feature_deltas.items():
                if f_val is None: continue
                
                key = (lever, p_name, p_val, f_name)
                if key not in groups:
                    groups[key] = {
                        "pass": 0, "partial": 0, "fail": 0, "values": [],
                        "trace": {"s": set(), "k": set(), "e": set(), "x": set()}
                    }
                    
                g = groups[key]
                g["values"].append(f_val)
                
                if decision == "PASS": g["pass"] += 1
                elif decision == "PARTIAL_PASS": g["partial"] += 1
                else: g["fail"] += 1
                
                if s_id: g["trace"]["s"].add(s_id)
                if k_id: g["trace"]["k"].add(k_id)
                if e_id: g["trace"]["e"].add(e_id)
                if x_id: g["trace"]["x"].add(x_id)
                
    aggregated = []
    for (lever, p_name, p_val, f_name), g in groups.items():
        vals = sorted(g["values"])
        support = len(vals)
        
        mean_val = sum(vals) / support if support > 0 else 0
        median_val = vals[support//2] if support > 0 else 0
        
        var = sum((v - mean_val)**2 for v in vals) / support if support > 0 else 0
        std = math.sqrt(var)
        min_v = vals[0] if support > 0 else 0
        max_v = vals[-1] if support > 0 else 0
        
        hist = {b: 0 for b in HISTOGRAM_BINS}
        hist["<0.0"] = 0
        hist[">=1.0"] = 0
        
        for v in vals:
            hist[get_bin(v)] += 1
            
        aggregated.append({
            "lever": lever, "parameter_name": p_name, "parameter_value": p_val, "feature_name": f_name,
            "support_count": support, "pass_count": g["pass"], "partial_count": g["partial"], "fail_count": g["fail"],
            "mean": round(mean_val, 6), "median": round(median_val, 6),
            "variance": round(var, 6), "std_dev": round(std, 6),
            "minimum": round(min_v, 6), "maximum": round(max_v, 6),
            "histogram": hist, "trace": g["trace"]
        })
        
    return aggregated
