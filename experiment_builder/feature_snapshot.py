"""
feature_snapshot.py
Captures and stores the acoustic feature state for one experiment.

Stores:
  - ref_features.json  : scalar features from reference audio
  - gen_features.json  : scalar features from generated audio
  - feature_vector.npy : numpy array [ref_vector (19,), gen_vector (19,),
                          diff_vector (19,)]  stacked as shape (3, 19)

No AI. No optimization. No recommendation.
Pure data capture.
"""

import json
import os
import numpy as np
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../benchmark")))
from feature_registry import FEATURE_REGISTRY, FEATURE_DIMENSION
from feature_vector import build_feature_vector

SNAPSHOT_VERSION = "1.0.0"


def capture_feature_snapshot(experiment_dir, ref_scalars, gen_scalars):
    """
    Captures the feature state for one experiment and writes to disk.

    Args:
        experiment_dir : str — target directory for this experiment
        ref_scalars    : dict — scalar feature values from reference audio
        gen_scalars    : dict — scalar feature values from generated audio

    Returns:
        dict with paths to saved files and array metadata
    """
    os.makedirs(experiment_dir, exist_ok=True)

    # 1. Save raw scalar dicts
    ref_path = os.path.join(experiment_dir, "ref_features.json")
    gen_path = os.path.join(experiment_dir, "gen_features.json")

    with open(ref_path, "w", encoding="utf-8") as f:
        json.dump({"snapshot_version": SNAPSHOT_VERSION, "features": ref_scalars}, f, indent=4)

    with open(gen_path, "w", encoding="utf-8") as f:
        json.dump({"snapshot_version": SNAPSHOT_VERSION, "features": gen_scalars}, f, indent=4)

    # 2. Build numerical vectors
    ref_vector  = build_feature_vector(ref_scalars)   # shape (19,)
    gen_vector  = build_feature_vector(gen_scalars)   # shape (19,)
    diff_vector = gen_vector - ref_vector              # shape (19,)

    # Stack into (3, 19) array: [ref, gen, diff]
    stacked = np.stack([ref_vector, gen_vector, diff_vector], axis=0)

    npy_path = os.path.join(experiment_dir, "feature_vector.npy")
    np.save(npy_path, stacked)

    return {
        "ref_features_path":  ref_path,
        "gen_features_path":  gen_path,
        "feature_vector_path": npy_path,
        "vector_shape":        list(stacked.shape),   # [3, 19]
        "feature_registry":    FEATURE_REGISTRY,
        "feature_dimension":   FEATURE_DIMENSION
    }
