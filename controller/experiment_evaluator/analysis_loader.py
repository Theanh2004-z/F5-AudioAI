"""
analysis_loader.py
Loads analysis_registry.json and selects analyses ready for evaluation.
Selects only VALIDATED (or COMPLETED) analyses.
Never modifies registry records.
"""

import json
import os

def load_pending_analyses(analysis_registry_path, evaluation_registry_path):
    """
    Loads analysis registry and returns a list of records that need evaluation.
    
    Args:
        analysis_registry_path: Path to analysis_registry.json
        evaluation_registry_path: Path to evaluation_registry.json
        
    Returns:
        list: Analysis records ready for evaluation.
    """
    if not os.path.exists(analysis_registry_path):
        print(f"[AnalysisLoader] WARNING: Analysis registry not found at {analysis_registry_path}")
        return []
        
    with open(analysis_registry_path, "r", encoding="utf-8") as f:
        analysis_registry = json.load(f)
        
    # Load evaluation registry to filter out already evaluated ones
    evaluated_analysis_ids = set()
    if os.path.exists(evaluation_registry_path):
        with open(evaluation_registry_path, "r", encoding="utf-8") as f:
            eval_registry = json.load(f)
            for r in eval_registry.get("records", []):
                evaluated_analysis_ids.add(r["analysis_id"])
                
    runnable = []
    for record in analysis_registry.get("records", []):
        status = record.get("analysis_status")
        # Accept COMPLETED or VALIDATED to support pipeline handoff
        if status in ["VALIDATED", "COMPLETED"]:
            if record["analysis_id"] not in evaluated_analysis_ids:
                runnable.append(record)
                
    print(f"[AnalysisLoader] Found {len(runnable)} analyses ready for evaluation.")
    return runnable
