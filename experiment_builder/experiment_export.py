"""
experiment_export.py
Exports the complete unified dataset from all logged experiments.

Outputs (written to dataset/):
  - training_dataset.jsonl    : one JSON object per line, one per experiment
  - training_dataset.npy      : structured numpy archive (feat_matrix, param_matrix, ids)
  - dataset_statistics.json   : summary statistics over the assembled dataset

No AI. No optimization. No recommendation.
Pure serialization and statistical description.
"""

import json
import os
import sys
import numpy as np
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from dataset_builder import build_dataset, FLAT_FEATURE_DIMENSION
from sample_registry import SampleRegistry, DATASET_VERSION
from parameter_snapshot import PARAMETER_REGISTRY_ORDERED, PARAMETER_DIMENSION

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../benchmark")))
from feature_registry import FEATURE_REGISTRY, FEATURE_DIMENSION

EXPORT_VERSION = "1.0.0"


def _compute_statistics(samples, feat_matrix, param_matrix):
    """
    Computes descriptive statistics over the dataset.
    No scoring. No inference. Pure description.
    """
    n = len(samples)
    if n == 0:
        return {"total_samples": 0, "note": "No samples to compute statistics."}

    provenance_counts = {}
    for s in samples:
        p = s.get("provenance", "unknown")
        provenance_counts[p] = provenance_counts.get(p, 0) + 1

    # Feature statistics: diff_vector is rows [2*FEATURE_DIMENSION : 3*FEATURE_DIMENSION]
    diff_slice = feat_matrix[:, FEATURE_DIMENSION * 2:]  # shape (N, 19)

    feature_stats = {}
    for i, feat_name in enumerate(FEATURE_REGISTRY):
        col = diff_slice[:, i]
        feature_stats[feat_name] = {
            "mean":   float(np.mean(col)),
            "std":    float(np.std(col)),
            "min":    float(np.min(col)),
            "max":    float(np.max(col)),
            "median": float(np.median(col))
        }

    # Parameter statistics
    param_stats = {}
    for i, param_name in enumerate(PARAMETER_REGISTRY_ORDERED):
        col = param_matrix[:, i]
        param_stats[param_name] = {
            "mean":   float(np.mean(col)),
            "std":    float(np.std(col)),
            "min":    float(np.min(col)),
            "max":    float(np.max(col)),
            "median": float(np.median(col))
        }

    return {
        "total_samples":         n,
        "provenance_breakdown":  provenance_counts,
        "feature_diff_statistics": feature_stats,
        "parameter_statistics":  param_stats,
        "matrix_shapes": {
            "feat_matrix":  list(feat_matrix.shape),
            "param_matrix": list(param_matrix.shape)
        }
    }


def export_dataset(dataset_dir="dataset"):
    """
    Runs the full export pipeline.

    Args:
        dataset_dir : str — dataset root directory

    Returns:
        dict of output file paths
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs(dataset_dir, exist_ok=True)

    # 1. Build in-memory dataset
    print("Building dataset from registry...")
    samples, feat_matrix, param_matrix, errors = build_dataset(dataset_dir)
    n = len(samples)
    print(f"  Loaded {n} samples | {len(errors)} errors")

    # 2. Export training_dataset.jsonl
    jsonl_path = os.path.join(dataset_dir, "training_dataset.jsonl")
    with open(jsonl_path, "w", encoding="utf-8") as f:
        for sample in samples:
            f.write(json.dumps(sample, ensure_ascii=False) + "\n")

    # 3. Export training_dataset.npy (structured archive)
    npy_path = os.path.join(dataset_dir, "training_dataset.npy")
    experiment_ids = np.array([s["experiment_id"] for s in samples])
    np.save(npy_path, {
        "feat_matrix":          feat_matrix,        # (N, 57)  float32
        "param_matrix":         param_matrix,       # (N, 6)   float32
        "experiment_ids":       experiment_ids,     # (N,)     str
        "feature_registry":     FEATURE_REGISTRY,
        "parameter_registry":   PARAMETER_REGISTRY_ORDERED,
        "flat_feature_dimension": FLAT_FEATURE_DIMENSION,
        "parameter_dimension":  PARAMETER_DIMENSION,
        "export_version":       EXPORT_VERSION,
        "timestamp":            timestamp
    })

    # 4. Export dataset_statistics.json
    stats = _compute_statistics(samples, feat_matrix, param_matrix)
    stats["export_version"]     = EXPORT_VERSION
    stats["dataset_version"]    = DATASET_VERSION
    stats["export_timestamp"]   = timestamp
    stats["errors"]             = errors

    stats_path = os.path.join(dataset_dir, "dataset_statistics.json")
    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=4)

    output_paths = {
        "training_dataset.jsonl":  jsonl_path,
        "training_dataset.npy":    npy_path,
        "dataset_statistics.json": stats_path
    }

    print(f"\n✅ Export complete ({n} samples)")
    for name, path in output_paths.items():
        print(f"  {name:35s} → {path}")

    return output_paths


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="F5-TTS Experiment Dataset Exporter")
    parser.add_argument("--dataset_dir", type=str, default="dataset", help="Dataset root directory")
    args = parser.parse_args()
    export_dataset(args.dataset_dir)
