"""
parameter_snapshot.py
Captures and stores the F5-TTS inference parameter values used for one experiment.

Stores:
  - parameters.json        : full parameter values + provenance
  - parameter_vector.npy   : fixed-order numeric array for ML consumption

No AI. No optimization. No recommendation.
Pure data capture.
"""

import json
import os
import numpy as np

SNAPSHOT_VERSION = "1.0.0"

# Fixed ordered list of parameters. ORDER MUST NOT CHANGE between versions.
# Adding new parameters requires a version bump.
PARAMETER_REGISTRY_ORDERED = [
    "speed",
    "target_rms",
    "cfg_strength",
    "nfe_step",
    "sway_sampling_coef",
    "cross_fade_duration"
]

PARAMETER_DEFAULTS = {
    "speed":               1.0,
    "target_rms":          0.1,
    "cfg_strength":        2.0,
    "nfe_step":            32,
    "sway_sampling_coef":  -1.0,
    "cross_fade_duration": 0.15
}

PARAMETER_DIMENSION = len(PARAMETER_REGISTRY_ORDERED)


def capture_parameter_snapshot(experiment_dir, parameter_values=None, provenance="default"):
    """
    Captures the inference parameter state and writes to disk.

    Args:
        experiment_dir   : str  — target directory for this experiment
        parameter_values : dict — actual values used (None = use defaults)
        provenance       : str  — "default" | "manual" | "ai_controller"

    Returns:
        dict with paths and metadata
    """
    os.makedirs(experiment_dir, exist_ok=True)

    # Merge provided values with defaults
    params = dict(PARAMETER_DEFAULTS)
    if parameter_values:
        params.update({k: v for k, v in parameter_values.items() if k in params})

    # Build ordered numeric vector
    param_vector = np.array(
        [float(params[k]) for k in PARAMETER_REGISTRY_ORDERED],
        dtype=np.float32
    )

    # Save JSON
    json_payload = {
        "snapshot_version":          SNAPSHOT_VERSION,
        "provenance":                provenance,
        "parameter_registry_ordered": PARAMETER_REGISTRY_ORDERED,
        "parameter_dimension":        PARAMETER_DIMENSION,
        "values":                    params
    }
    json_path = os.path.join(experiment_dir, "parameters.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_payload, f, indent=4)

    # Save NPY
    npy_path = os.path.join(experiment_dir, "parameter_vector.npy")
    np.save(npy_path, param_vector)

    return {
        "parameters_path":        json_path,
        "parameter_vector_path":  npy_path,
        "parameter_dimension":    PARAMETER_DIMENSION,
        "provenance":             provenance,
        "values":                 params
    }
