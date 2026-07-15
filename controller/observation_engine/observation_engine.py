"""
observation_engine.py — Main Orchestrator

Input:
  - feature_vector.npy (raw npy dict with ref_vector / gen_vector)
  - report.json         (full report from benchmark pipeline)

Output:
  - normalized_feature_difference.json
  - observation_report.json
  - confidence_report.json

This engine may ONLY:
  - normalize values
  - estimate measurement confidence
  - classify observation quality
  - attach metadata
  - detect missing or invalid features

It MUST NOT:
  - recommend parameters
  - modify F5 settings
  - use thresholds to tune parameters
  - contain expert-system logic
  - infer causal relationships
"""

import json
import os
import sys
import numpy as np
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from feature_validator import validate_features
from normalizer import normalize_all_differences
from confidence_estimator import build_confidence_report
from observation_classifier import classify_all_observations


OBSERVATION_ENGINE_VERSION = "1.0.0"


def run_observation_engine(report_path, output_dir="."):
    """
    Main entry point.

    Args:
        report_path : str  — path to report.json from benchmark pipeline
        output_dir  : str  — directory to write the 3 output files

    Returns:
        dict of output file paths
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # -----------------------------------------------------------------------
    # 1. Load report.json
    # -----------------------------------------------------------------------
    with open(report_path, "r", encoding="utf-8") as f:
        report = json.load(f)

    ref_scalars = report.get("reference", {})
    gen_scalars = report.get("generated", {})
    metadata    = report.get("metadata", {})

    # -----------------------------------------------------------------------
    # 2. Validate features (detect missing / invalid)
    # -----------------------------------------------------------------------
    ref_issues, ref_valid = validate_features(ref_scalars)
    gen_issues, gen_valid = validate_features(gen_scalars)
    all_issues = (
        [{"source": "reference", **i} for i in ref_issues] +
        [{"source": "generated", **i} for i in gen_issues]
    )

    # -----------------------------------------------------------------------
    # 3. Normalize differences
    # -----------------------------------------------------------------------
    normalized_diffs = normalize_all_differences(ref_scalars, gen_scalars)

    # -----------------------------------------------------------------------
    # 4. Estimate confidence
    # -----------------------------------------------------------------------
    confidence_report = build_confidence_report(ref_scalars, gen_scalars, all_issues)

    # -----------------------------------------------------------------------
    # 5. Classify observations
    # -----------------------------------------------------------------------
    classifications = classify_all_observations(ref_scalars, gen_scalars, confidence_report)

    # -----------------------------------------------------------------------
    # 6. Attach metadata and assemble outputs
    # -----------------------------------------------------------------------
    engine_metadata = {
        "observation_engine_version": OBSERVATION_ENGINE_VERSION,
        "timestamp": timestamp,
        "benchmark_metadata": metadata,
        "validation_summary": {
            "reference_valid": ref_valid,
            "generated_valid": gen_valid,
            "total_issues": len(all_issues)
        }
    }

    normalized_diff_doc = {
        "metadata": engine_metadata,
        "normalized_feature_difference": normalized_diffs
    }

    observation_doc = {
        "metadata": engine_metadata,
        "validation_issues": all_issues,
        "classifications": classifications
    }

    confidence_doc = {
        "metadata": engine_metadata,
        "confidence_report": confidence_report
    }

    # -----------------------------------------------------------------------
    # 7. Export
    # -----------------------------------------------------------------------
    os.makedirs(output_dir, exist_ok=True)

    paths = {}
    exports = {
        "normalized_feature_difference.json": normalized_diff_doc,
        "observation_report.json":            observation_doc,
        "confidence_report.json":             confidence_doc,
    }

    for filename, content in exports.items():
        p = os.path.join(output_dir, filename)
        with open(p, "w", encoding="utf-8") as f:
            json.dump(content, f, indent=4)
        paths[filename] = p
        print(f"  ✅ {p}")

    print(f"\n✅ Observation Engine complete — {len(paths)} files written to '{output_dir}'")
    return paths


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="F5-TTS Observation Engine")
    parser.add_argument("--report",     type=str, required=True, help="Path to report.json")
    parser.add_argument("--output_dir", type=str, default=".",   help="Output directory")
    args = parser.parse_args()

    run_observation_engine(args.report, args.output_dir)
