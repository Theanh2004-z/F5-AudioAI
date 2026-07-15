"""
learning_builder.py
"""
import uuid
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from evidence_strength import lookup_evidence_strength

def build_learning_records(aggregated_data, metadata_versions):
    pivot = {}
    for item in aggregated_data:
        key = (item["lever"], item["parameter_name"], item["parameter_value"])
        if key not in pivot:
            pivot[key] = {
                "features": {},
                "trace": {"s": set(), "k": set(), "e": set(), "x": set()}
            }
        
        f_name = item["feature_name"]
        pivot[key]["features"][f_name] = {
            "support_count": item["support_count"],
            "pass_count": item["pass_count"],
            "partial_count": item["partial_count"],
            "fail_count": item["fail_count"],
            "mean": item["mean"],
            "median": item["median"],
            "variance": item["variance"],
            "std_dev": item["std_dev"],
            "minimum": item["minimum"],
            "maximum": item["maximum"],
            "evidence_strength": lookup_evidence_strength(item["support_count"]),
            "histogram": item["histogram"]
        }
        
        pivot[key]["trace"]["s"].update(item["trace"]["s"])
        pivot[key]["trace"]["k"].update(item["trace"]["k"])
        pivot[key]["trace"]["e"].update(item["trace"]["e"])
        pivot[key]["trace"]["x"].update(item["trace"]["x"])
        
    records = []
    for key in sorted(pivot.keys()):
        lever, p_name, p_val = key
        data = pivot[key]
        
        record = {
            "learning_record_id": f"LRN-{uuid.uuid4().hex[:8].upper()}",
            "metadata": {
                "lever": lever,
                "parameter_name": p_name,
                "parameter_value": p_val
            },
            "feature_statistics": {},
            "traceability": {
                "source_sample_ids": sorted(list(data["trace"]["s"])),
                "source_knowledge_ids": sorted(list(data["trace"]["k"])),
                "source_evaluation_ids": sorted(list(data["trace"]["e"])),
                "source_experiment_ids": sorted(list(data["trace"]["x"])),
                "dataset_version": metadata_versions.get("dataset_version", "1.0.0"),
                "dataset_manifest_version": metadata_versions.get("dataset_manifest_version", "1.0.0"),
                "curation_version": metadata_versions.get("curation_version", "1.0.0"),
                "curation_manifest_version": metadata_versions.get("curation_manifest_version", "1.0.0"),
                "knowledge_snapshot_version": metadata_versions.get("knowledge_snapshot_version", "1.0.0")
            }
        }
        
        for f_name in sorted(data["features"].keys()):
            record["feature_statistics"][f_name] = data["features"][f_name]
            
        records.append(record)
        
    return records
