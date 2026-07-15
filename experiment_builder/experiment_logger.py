"""
experiment_logger.py
Main entry point for recording one complete experiment run.

Orchestrates:
  1. Assign experiment ID via SampleRegistry
  2. Create experiment directory
  3. Capture feature snapshot (feature_snapshot.py)
  4. Capture parameter snapshot (parameter_snapshot.py)
  5. Copy / reference benchmark report
  6. Write experiment_manifest.json
  7. Register in SampleRegistry

No AI. No optimization. No recommendation.
Pure data collection pipeline.
"""

import json
import os
import sys
import platform
import shutil
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from sample_registry import SampleRegistry
from feature_snapshot import capture_feature_snapshot
from parameter_snapshot import capture_parameter_snapshot

EXPERIMENT_BUILDER_VERSION = "1.0.0"


def _collect_runtime_metadata():
    """Collects platform / environment info — purely descriptive."""
    return {
        "platform":        platform.system(),
        "platform_release": platform.release(),
        "python_version":  platform.python_version(),
        "hostname":        platform.node()
    }


def log_experiment(
    ref_scalars,
    gen_scalars,
    benchmark_report_path,
    dataset_dir     = "dataset",
    parameter_values = None,
    provenance       = "default",
    inference_metadata = None,
    observation_report_path = None
):
    """
    Records one complete experiment to the dataset.

    Args:
        ref_scalars              : dict — reference audio scalar features
        gen_scalars              : dict — generated audio scalar features
        benchmark_report_path    : str  — path to report.json from benchmark
        dataset_dir              : str  — root dataset directory
        parameter_values         : dict — inference parameters used (None = defaults)
        provenance               : str  — "default" | "manual" | "ai_controller"
        inference_metadata       : dict — arbitrary inference context (audio paths, etc.)
        observation_report_path  : str  — optional path to observation_report.json

    Returns:
        dict — experiment manifest
    """
    registry       = SampleRegistry(dataset_dir)
    experiment_id  = registry.next_experiment_id()
    experiment_dir = os.path.join(dataset_dir, experiment_id)
    os.makedirs(experiment_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 1. Feature snapshot
    feat_meta = capture_feature_snapshot(experiment_dir, ref_scalars, gen_scalars)

    # 2. Parameter snapshot
    param_meta = capture_parameter_snapshot(experiment_dir, parameter_values, provenance)

    # 3. Benchmark report
    report_dest = os.path.join(experiment_dir, "benchmark_report.json")
    if benchmark_report_path and os.path.exists(benchmark_report_path):
        shutil.copy2(benchmark_report_path, report_dest)
    else:
        report_dest = None

    # 4. Observation report (optional)
    obs_dest = None
    if observation_report_path and os.path.exists(observation_report_path):
        obs_dest = os.path.join(experiment_dir, "observation_report.json")
        shutil.copy2(observation_report_path, obs_dest)

    # 5. Assemble manifest
    manifest = {
        "experiment_id":             experiment_id,
        "experiment_builder_version": EXPERIMENT_BUILDER_VERSION,
        "timestamp":                 timestamp,
        "inference_metadata":        inference_metadata or {},
        "runtime_metadata":          _collect_runtime_metadata(),
        "feature_snapshot":          feat_meta,
        "parameter_snapshot":        param_meta,
        "benchmark_report_path":     report_dest,
        "observation_report_path":   obs_dest,
        "files": {
            "ref_features":       feat_meta["ref_features_path"],
            "gen_features":       feat_meta["gen_features_path"],
            "feature_vector":     feat_meta["feature_vector_path"],
            "parameters":         param_meta["parameters_path"],
            "parameter_vector":   param_meta["parameter_vector_path"],
            "benchmark_report":   report_dest,
            "observation_report": obs_dest
        }
    }

    manifest_path = os.path.join(experiment_dir, "experiment_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=4)

    # 6. Register
    registry.register(experiment_id, experiment_dir, {
        "timestamp":  timestamp,
        "provenance": provenance,
        "manifest":   manifest_path
    })

    print(f"✅ Logged: {experiment_id} → {experiment_dir}")
    return manifest
