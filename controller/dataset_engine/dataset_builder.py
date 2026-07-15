"""
dataset_builder.py
Performs technical deduplication and deterministic sorting of samples.
"""

def build_dataset_samples(consolidated_samples):
    """
    Filters pipeline retries (same knowledge/eval/exp IDs) and sorts deterministically.
    """
    unique_samples = []
    seen_ids = set()
    
    for sample in consolidated_samples:
        # Technical deduplication key
        k_id = sample.get("knowledge_id", "")
        e_id = sample.get("evaluation_id", "")
        x_id = sample.get("experiment_id", "")
        dedupe_key = f"{k_id}|{e_id}|{x_id}"
        
        if dedupe_key in seen_ids:
            continue
            
        seen_ids.add(dedupe_key)
        unique_samples.append(sample)
        
    # Deterministic Sort: experiment_id -> evaluation_id -> knowledge_id
    unique_samples.sort(key=lambda s: (
        s.get("experiment_id", ""),
        s.get("evaluation_id", ""),
        s.get("knowledge_id", "")
    ))
    
    return unique_samples
