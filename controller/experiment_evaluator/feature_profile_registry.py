"""
feature_profile_registry.py
Defines evaluation profiles for specific features.
Includes thresholds, directions, and importance levels (LOW, MEDIUM, HIGH, CRITICAL).
"""

FEATURE_PROFILE_VERSION = "1.0.0"

# Direction constants
DIR_LOWER_IS_BETTER = "LOWER_IS_BETTER"
DIR_HIGHER_IS_BETTER = "HIGHER_IS_BETTER"
DIR_CLOSER_IS_BETTER = "CLOSER_IS_BETTER" # i.e. delta towards 0

# Default profile if feature not specifically mapped
DEFAULT_PROFILE = {
    "feature": "unknown",
    "improved_threshold": 0.05,
    "degraded_threshold": 0.05,
    "direction": DIR_CLOSER_IS_BETTER,
    "importance": "LOW"
}

# In a real integration, this maps feature indices or names to profiles.
# Since we receive a feature vector (indices), we'll map by index for now,
# but architecturally it should map by feature name. We'll use a mocked map by index.
FEATURE_PROFILES = {
    0: {
        "feature": "pitch_f0_mean",
        "improved_threshold": 0.03,
        "degraded_threshold": 0.03,
        "direction": DIR_CLOSER_IS_BETTER,
        "importance": "HIGH"
    },
    1: {
        "feature": "energy_rms_mean",
        "improved_threshold": 0.05,
        "degraded_threshold": 0.05,
        "direction": DIR_CLOSER_IS_BETTER,
        "importance": "MEDIUM"
    },
    2: {
        "feature": "speech_rate",
        "improved_threshold": 0.02,
        "degraded_threshold": 0.02,
        "direction": DIR_CLOSER_IS_BETTER,
        "importance": "CRITICAL"
    }
}

def get_feature_profile(feature_identifier):
    """
    Retrieves the feature profile for a given feature index or name.
    """
    return FEATURE_PROFILES.get(feature_identifier, DEFAULT_PROFILE)
