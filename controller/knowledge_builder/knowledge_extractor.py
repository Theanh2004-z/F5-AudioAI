"""
knowledge_extractor.py
Extracts raw knowledge data from evaluation artifacts.
No reasoning, no causality inference, no recommendations.
Only reads files and reshapes data into knowledge record format.
"""

import json
import os

def extract_knowledge(eval_record, eval_dir):
    """
    Reads evaluation artifacts and extracts data for the knowledge record.
    
    Args:
        eval_record: Row from evaluation_registry.json.
        eval_dir: Path to the evaluation artifact directory.
        
    Returns:
        dict: Raw knowledge extraction data.
    """
    knowledge_data = {
        "evaluation_id":  eval_record.get("evaluation_id"),
        "experiment_id":  eval_record.get("experiment_id", "UNKNOWN"),
        "analysis_id":    eval_record.get("analysis_id", "UNKNOWN"),
        "benchmark_id":   eval_record.get("benchmark_id", "UNKNOWN"),
        "execution_id":   eval_record.get("execution_id", "UNKNOWN"),
        "decision":       eval_record.get("decision"),
        "lever":          "UNKNOWN",
        "observed_features": [],
        "baseline_id":    "UNKNOWN"
    }

    # -- Read scorecard for per-feature outcomes
    scorecard_path = os.path.join(eval_dir, "scorecard.json")
    if os.path.exists(scorecard_path):
        with open(scorecard_path, "r", encoding="utf-8") as f:
            scorecard = json.load(f)
        knowledge_data["observed_features"] = scorecard.get("feature_evaluations", [])

    # -- Read manifest for traceability and baseline
    manifest_path = os.path.join(eval_dir, "evaluation_manifest.json")
    if os.path.exists(manifest_path):
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
        trace = manifest.get("traceability", {})
        knowledge_data["baseline_id"] = trace.get("baseline_id", "UNKNOWN")
        # Lever is stored in the experiment plan — we read it from manifest if propagated
        knowledge_data["lever"] = trace.get("lever", eval_record.get("experiment_id", "UNKNOWN"))

    return knowledge_data
