"""
confidence_estimator.py
Responsibility: Estimate per-feature measurement confidence.
Sources of confidence:
  - Analyzer-reported confidence (e.g., pitch_confidence from analyzers)
  - Validity of the extracted value (via feature_validator output)
  - Whether the value falls within expected_range

No parameter recommendation.
No causal inference.
No threshold-based tuning logic.
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../benchmark")))
from feature_registry import FEATURE_REGISTRY_METADATA

RANGE_LOOKUP = {
    feat["name"]: feat["expected_range"]
    for feat in FEATURE_REGISTRY_METADATA
}

GROUP_TO_ANALYZER_CONFIDENCE = {
    "Pitch":          "pitch_confidence",
    "Energy":         "energy_confidence",
    "Rhythm":         "rhythm_confidence",
    "Spectral":       "spectral_confidence",
    "Voice Quality":  "vq_confidence"
}

GROUP_LOOKUP = {
    feat["name"]: feat["group"]
    for feat in FEATURE_REGISTRY_METADATA
}


def estimate_feature_confidence(feature_name, value, ref_scalars, validation_issues):
    """
    Returns a confidence score in [0, 1] for one feature.
    Factors:
      1. Analyzer confidence (from ref_scalars)
      2. In-range check (is value within expected_range?)
      3. Validation issue severity (penalty)
    """

    # 1. Base from analyzer confidence (if available)
    group = GROUP_LOOKUP.get(feature_name)
    conf_key = GROUP_TO_ANALYZER_CONFIDENCE.get(group)
    base_confidence = ref_scalars.get(conf_key, 1.0) if conf_key else 1.0

    # 2. In-range penalty
    range_penalty = 0.0
    if feature_name in RANGE_LOOKUP and value is not None:
        lo, hi = RANGE_LOOKUP[feature_name]
        if value < lo or value > hi:
            range_penalty = 0.2  # Value outside expected_range reduces confidence

    # 3. Validation issue penalty
    issue_penalty = 0.0
    for issue in validation_issues:
        if issue["feature"] == feature_name:
            if issue["severity"] == "CRITICAL":
                issue_penalty = 1.0
            elif issue["severity"] == "HIGH":
                issue_penalty = 0.5
            elif issue["severity"] == "MEDIUM":
                issue_penalty = 0.2

    confidence = max(0.0, min(1.0, base_confidence - range_penalty - issue_penalty))
    return round(confidence, 4)


def build_confidence_report(ref_scalars, gen_scalars, validation_issues):
    """
    Builds a full per-feature confidence report for both ref and gen.
    Returns a dict keyed by feature name.
    """
    report = {}

    for feat in FEATURE_REGISTRY_METADATA:
        name = feat["name"]
        report[name] = {
            "ref_confidence": estimate_feature_confidence(
                name, ref_scalars.get(name), ref_scalars, validation_issues
            ),
            "gen_confidence": estimate_feature_confidence(
                name, gen_scalars.get(name), gen_scalars, validation_issues
            )
        }

    return report
