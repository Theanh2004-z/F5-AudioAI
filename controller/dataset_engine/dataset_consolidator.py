"""
dataset_consolidator.py
Flattens loaded knowledge artifacts into ML-ready Dataset Samples.
"""
import uuid
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from dataset_schema import DATASET_SCHEMA_VERSION

def consolidate_sample(record_metadata, know_data, know_prof, know_evid, manifest):
    """
    Transforms multiple artifacts into a single unified JSON sample.
    """
    sample_id = f"SAMP-{uuid.uuid4().hex[:8]}"
    traceability = manifest.get("traceability", {})
    
    # We construct the sample preserving all required schema fields
    sample = {
        "dataset_schema_version": DATASET_SCHEMA_VERSION,
        "sample_id": sample_id,
        "knowledge_id": record_metadata.get("knowledge_id", ""),
        "evaluation_id": record_metadata.get("evaluation_id", ""),
        "experiment_id": record_metadata.get("experiment_id", ""),
        "benchmark_id": traceability.get("benchmark_id", ""),
        "analysis_id": traceability.get("analysis_id", ""),
        "execution_id": traceability.get("execution_id", ""),
        "lever": record_metadata.get("lever", ""),
        "parameter_values": know_prof.get("parameters", {}), # Varies depending on how Stage 12 writes it
        "feature_deltas": know_prof.get("feature_deltas", {}),
        "observed_outcomes": know_evid.get("observed_outcomes", {}),
        "decision": record_metadata.get("decision", ""),
        "timestamp": manifest.get("timestamp", 0.0),
        "traceability": traceability
    }
    
    # Optional: Fill parameter_values if not inside knowledge_profile
    if not sample["parameter_values"]:
        # Fallback or empty dict if not explicitly separated
        pass

    return sample
