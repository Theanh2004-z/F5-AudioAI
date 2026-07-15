"""
dataset_builder.py
Assembles all logged experiments into a unified, ML-ready dataset.

Reads every experiment directory registered in sample_registry.json and
builds:
  - A flat list of training sample dicts (for JSONL)
  - A stacked numpy matrix (for NPY)
  - Dataset statistics

Each training sample has the schema:
{
    "experiment_id":      str,
    "timestamp":          str,
    "provenance":         str,
    "feature_vector":     list[float]  shape [3, 19] → flattened to [57]
                          [ref_vector | gen_vector | diff_vector]
    "parameter_vector":   list[float]  shape [6]
    "inference_metadata": dict,
    "runtime_metadata":   dict
}

No AI. No optimization. No recommendation.
Pure data assembly.
"""

import json
import os
import sys
import numpy as np
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from sample_registry import SampleRegistry
from parameter_snapshot import PARAMETER_REGISTRY_ORDERED, PARAMETER_DIMENSION

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../benchmark")))
from feature_registry import FEATURE_REGISTRY, FEATURE_DIMENSION

DATASET_BUILDER_VERSION = "1.0.0"

# The flat feature vector is: [ref(19) | gen(19) | diff(19)] = 57 dims
FLAT_FEATURE_DIMENSION = FEATURE_DIMENSION * 3  # 57


def _load_experiment_sample(experiment_entry):
    """
    Loads one experiment from its directory and builds the training sample dict.
    Returns None if any critical file is missing or unreadable.
    """
    exp_dir = experiment_entry.get("experiment_dir", "")
    exp_id  = experiment_entry["experiment_id"]

    manifest_path = os.path.join(exp_dir, "experiment_manifest.json")
    if not os.path.exists(manifest_path):
        return None, f"Missing manifest: {manifest_path}"

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    # Load feature vector (3, 19) → flatten to (57,)
    feat_npy = os.path.join(exp_dir, "feature_vector.npy")
    if not os.path.exists(feat_npy):
        return None, f"Missing feature_vector.npy in {exp_dir}"
    feat_array = np.load(feat_npy)               # shape (3, 19)
    flat_feat  = feat_array.flatten().tolist()   # list[57]

    # Load parameter vector (6,)
    param_npy = os.path.join(exp_dir, "parameter_vector.npy")
    if not os.path.exists(param_npy):
        return None, f"Missing parameter_vector.npy in {exp_dir}"
    param_array = np.load(param_npy)             # shape (6,)
    param_list  = param_array.tolist()           # list[6]

    sample = {
        "experiment_id":      exp_id,
        "timestamp":          manifest.get("timestamp", ""),
        "provenance":         manifest.get("parameter_snapshot", {}).get("provenance", "unknown"),
        "feature_vector":     flat_feat,
        "feature_registry":   FEATURE_REGISTRY,
        "parameter_vector":   param_list,
        "parameter_registry": PARAMETER_REGISTRY_ORDERED,
        "inference_metadata": manifest.get("inference_metadata", {}),
        "runtime_metadata":   manifest.get("runtime_metadata", {}),
        "schema": {
            "flat_feature_dimension": FLAT_FEATURE_DIMENSION,
            "parameter_dimension":    PARAMETER_DIMENSION,
            "feature_layout":         ["ref_vector", "gen_vector", "diff_vector"]
        }
    }

    return sample, None


def build_dataset(dataset_dir="dataset"):
    """
    Iterates over all registered experiments and assembles the training dataset.

    Returns:
        samples   : list[dict]
        feat_matrix  : np.ndarray shape (N, 57)
        param_matrix : np.ndarray shape (N, 6)
        errors    : list[str]
    """
    registry = SampleRegistry(dataset_dir)
    all_entries = registry.get_all()

    samples      = []
    feat_rows    = []
    param_rows   = []
    errors       = []

    for entry in all_entries:
        sample, err = _load_experiment_sample(entry)
        if err:
            errors.append({"experiment_id": entry.get("experiment_id"), "error": err})
            continue

        samples.append(sample)
        feat_rows.append(sample["feature_vector"])
        param_rows.append(sample["parameter_vector"])

    feat_matrix  = np.array(feat_rows,  dtype=np.float32) if feat_rows  else np.empty((0, FLAT_FEATURE_DIMENSION))
    param_matrix = np.array(param_rows, dtype=np.float32) if param_rows else np.empty((0, PARAMETER_DIMENSION))

    return samples, feat_matrix, param_matrix, errors
