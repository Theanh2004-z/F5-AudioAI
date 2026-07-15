"""
feature_delta_calculator.py
Calculates deltas between reference and generated features.
No reasoning or inference. Deterministic math only.
"""

import numpy as np
import os
import json

def calculate_feature_deltas(benchmark_dir, reference_feature_vector=None):
    """
    Calculates the delta between the benchmarked feature_vector.npy and a reference.
    
    Args:
        benchmark_dir: Path to the benchmark directory containing feature_vector.npy.
        reference_feature_vector: Path to the reference npy. If None, uses a dummy zero vector.
        
    Returns:
        dict: A dictionary of feature deltas.
    """
    target_path = os.path.join(benchmark_dir, "feature_vector.npy")
    
    if not os.path.exists(target_path):
        raise FileNotFoundError(f"[FeatureDeltaCalculator] feature_vector.npy not found in {benchmark_dir}")
        
    generated_features = np.load(target_path)
    
    if reference_feature_vector and os.path.exists(reference_feature_vector):
        ref_features = np.load(reference_feature_vector)
    else:
        # For offline infrastructure testing without a provided reference feature vector,
        # we assume a zero vector of the same shape to avoid breaking the pipeline.
        ref_features = np.zeros_like(generated_features)
        
    # Ensure shapes match
    if ref_features.shape != generated_features.shape:
        # In a real pipeline, we might slice or pad, but for now we raise or slice to minimum length.
        min_len = min(ref_features.shape[0], generated_features.shape[0])
        ref_features = ref_features[:min_len]
        generated_features = generated_features[:min_len]
        
    # Calculate absolute and relative deltas
    absolute_delta = generated_features - ref_features
    
    # Avoid division by zero
    with np.errstate(divide='ignore', invalid='ignore'):
        relative_delta = absolute_delta / ref_features
        relative_delta[~np.isfinite(relative_delta)] = 0.0 # Replace inf/nan with 0.0
        
    # We output a dictionary mapping feature indices to deltas
    # In a full integration, we would map this to feature_registry names.
    delta_dict = {
        "absolute_deltas": absolute_delta.tolist(),
        "relative_deltas": relative_delta.tolist(),
        "vector_size": int(generated_features.shape[0])
    }
    
    return delta_dict
