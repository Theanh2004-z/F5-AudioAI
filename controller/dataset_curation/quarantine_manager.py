"""
quarantine_manager.py
Logs discarded samples traceably.
"""
import os
import json
import time

def add_to_quarantine(sample, reasons, status):
    return {
        "sample_id": sample.get("sample_id", "UNKNOWN"),
        "knowledge_id": sample.get("knowledge_id", "UNKNOWN"),
        "evaluation_id": sample.get("evaluation_id", "UNKNOWN"),
        "experiment_id": sample.get("experiment_id", "UNKNOWN"),
        "dataset_quality_status": status,
        "reason_codes": reasons,
        "timestamp": time.time()
    }
    
def export_quarantine(quarantine_records, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, "quarantine_dataset.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(quarantine_records, f, indent=4)
