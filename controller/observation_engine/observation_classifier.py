"""
observation_classifier.py
Responsibility: Classify the quality of each observation.
Classifications are purely descriptive labels.

VALID            : Value present, in range, high confidence.
LOW_CONFIDENCE   : Value present but confidence < 0.6.
OUT_OF_RANGE     : Value present but outside expected_range.
SUSPECT          : Zero in a non-zero feature, or very close to boundary.
INVALID          : NaN, Inf, or extraction failure.
MISSING          : Feature not present in input.

No parameter recommendation.
No tuning logic.
No causal inference.
"""

import math
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../benchmark")))
from feature_registry import FEATURE_REGISTRY_METADATA

RANGE_LOOKUP = {
    feat["name"]: feat["expected_range"]
    for feat in FEATURE_REGISTRY_METADATA
}


def classify_observation(feature_name, value, confidence):
    """
    Returns a quality label for one feature observation.
    """
    if value is None:
        return "MISSING"

    if not isinstance(value, (int, float)):
        return "INVALID"

    if math.isnan(value) or math.isinf(value):
        return "INVALID"

    if feature_name in RANGE_LOOKUP:
        lo, hi = RANGE_LOOKUP[feature_name]
        if value < lo or value > hi:
            return "OUT_OF_RANGE"

    if confidence < 0.4:
        return "INVALID"

    if confidence < 0.6:
        return "LOW_CONFIDENCE"

    return "VALID"


def classify_all_observations(ref_scalars, gen_scalars, confidence_report):
    """
    Runs classify_observation for every registered feature on both ref and gen.
    Returns a nested dict: { feature_name: { "ref": label, "gen": label } }
    """
    classifications = {}

    for feat in FEATURE_REGISTRY_METADATA:
        name = feat["name"]
        ref_conf = confidence_report.get(name, {}).get("ref_confidence", 1.0)
        gen_conf = confidence_report.get(name, {}).get("gen_confidence", 1.0)

        classifications[name] = {
            "ref": classify_observation(name, ref_scalars.get(name), ref_conf),
            "gen": classify_observation(name, gen_scalars.get(name), gen_conf)
        }

    return classifications
