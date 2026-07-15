"""
normalizer.py
Responsibility: Normalize raw feature difference values to [-1, 1] using
the expected_range defined in the Feature Registry metadata.
No parameter recommendation. No expert-system logic. Pure math.
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../benchmark")))
from feature_registry import FEATURE_REGISTRY_METADATA


def _build_range_lookup():
    return {
        feat["name"]: feat["expected_range"]
        for feat in FEATURE_REGISTRY_METADATA
    }


RANGE_LOOKUP = _build_range_lookup()


def normalize_difference(ref_val, gen_val, feature_name):
    """
    Normalizes the raw difference (gen - ref) by the expected range span.
    Formula: normalized = (gen - ref) / (max - min)
    Clamped to [-1, 1].
    """
    raw_diff = gen_val - ref_val

    if feature_name not in RANGE_LOOKUP:
        return {
            "raw_difference": raw_diff,
            "normalized_difference": None,
            "status": "UNREGISTERED"
        }

    lo, hi = RANGE_LOOKUP[feature_name]
    span = hi - lo

    if span == 0:
        return {
            "raw_difference": raw_diff,
            "normalized_difference": None,
            "status": "ZERO_SPAN"
        }

    normalized = max(-1.0, min(1.0, raw_diff / span))

    return {
        "raw_difference": round(raw_diff, 6),
        "normalized_difference": round(normalized, 6),
        "expected_range": [lo, hi],
        "status": "OK"
    }


def normalize_all_differences(ref_scalars, gen_scalars):
    """
    Runs normalize_difference over all registered features.
    Returns a dict keyed by feature name.
    """
    result = {}
    all_features = list({**ref_scalars, **gen_scalars}.keys())

    for feature in all_features:
        ref_val = ref_scalars.get(feature, None)
        gen_val = gen_scalars.get(feature, None)

        if ref_val is None or gen_val is None:
            result[feature] = {
                "raw_difference": None,
                "normalized_difference": None,
                "status": "MISSING_VALUE"
            }
            continue

        result[feature] = normalize_difference(ref_val, gen_val, feature)

    return result
