"""
feature_validator.py
Responsibility: Detect missing, null, or numerically invalid features.
No parameter recommendation. No causal inference. No thresholds for tuning.
"""

import math

# These are the expected features as defined by the Feature Registry.
EXPECTED_FEATURES = [
    "pitch_f0_mean", "pitch_f0_variance", "pitch_voiced_ratio",
    "energy_rms_mean", "energy_rms_variance", "energy_peak", "energy_crest_factor",
    "rhythm_speech_duration", "rhythm_silence_duration", "rhythm_speech_rate",
    "rhythm_pause_count", "rhythm_mean_pause_duration",
    "spectral_centroid_mean", "spectral_rolloff_mean", "spectral_bandwidth_mean",
    "spectral_contrast_mean",
    "vq_zero_crossing_rate", "vq_spectral_flatness", "vq_harmonic_ratio"
]


def validate_features(feature_dict):
    """
    Checks the provided feature dict for:
    - Missing features (present in registry but absent in dict)
    - Null / NaN / Inf values
    - Zero-valued features that may indicate extraction failure

    Returns:
        issues  : list of dicts, each describing one issue
        is_valid: bool, True if no critical issues found
    """
    issues = []

    for feature in EXPECTED_FEATURES:
        if feature not in feature_dict:
            issues.append({
                "feature": feature,
                "severity": "CRITICAL",
                "type": "MISSING",
                "detail": "Feature not present in input dict."
            })
            continue

        val = feature_dict[feature]

        if val is None:
            issues.append({
                "feature": feature,
                "severity": "CRITICAL",
                "type": "NULL",
                "detail": "Feature value is null."
            })
        elif not isinstance(val, (int, float)):
            issues.append({
                "feature": feature,
                "severity": "CRITICAL",
                "type": "TYPE_ERROR",
                "detail": f"Expected numeric, got {type(val).__name__}."
            })
        elif math.isnan(val):
            issues.append({
                "feature": feature,
                "severity": "CRITICAL",
                "type": "NAN",
                "detail": "Feature value is NaN."
            })
        elif math.isinf(val):
            issues.append({
                "feature": feature,
                "severity": "HIGH",
                "type": "INF",
                "detail": "Feature value is Inf."
            })
        elif val == 0.0 and feature in [
            "pitch_f0_mean", "energy_rms_mean", "energy_peak",
            "rhythm_speech_duration", "rhythm_speech_rate"
        ]:
            issues.append({
                "feature": feature,
                "severity": "MEDIUM",
                "type": "ZERO_SUSPECT",
                "detail": "Value is zero in a feature where zero likely indicates extraction failure."
            })

    critical = any(i["severity"] == "CRITICAL" for i in issues)
    return issues, not critical
