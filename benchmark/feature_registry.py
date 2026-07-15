# Central registry defining the strict order of features in the feature vector.
# Each feature now includes extensive metadata for future AI consumption.

FEATURE_REGISTRY_METADATA = [
    {
        "name": "pitch_f0_mean",
        "group": "Pitch",
        "unit": "Hz",
        "expected_range": [50, 500],
        "dependency": []
    },
    {
        "name": "pitch_f0_variance",
        "group": "Pitch",
        "unit": "Hz^2",
        "expected_range": [0, 5000],
        "dependency": ["pitch_f0_mean"]
    },
    {
        "name": "pitch_voiced_ratio",
        "group": "Pitch",
        "unit": "ratio",
        "expected_range": [0.0, 1.0],
        "dependency": []
    },
    {
        "name": "energy_rms_mean",
        "group": "Energy",
        "unit": "amplitude",
        "expected_range": [0.0, 1.0],
        "dependency": []
    },
    {
        "name": "energy_rms_variance",
        "group": "Energy",
        "unit": "amplitude^2",
        "expected_range": [0.0, 1.0],
        "dependency": ["energy_rms_mean"]
    },
    {
        "name": "energy_peak",
        "group": "Energy",
        "unit": "amplitude",
        "expected_range": [0.0, 1.0],
        "dependency": []
    },
    {
        "name": "energy_crest_factor",
        "group": "Energy",
        "unit": "ratio",
        "expected_range": [1.0, 20.0],
        "dependency": ["energy_peak", "energy_rms_mean"]
    },
    {
        "name": "rhythm_speech_duration",
        "group": "Rhythm",
        "unit": "seconds",
        "expected_range": [0.0, 3600.0],
        "dependency": []
    },
    {
        "name": "rhythm_silence_duration",
        "group": "Rhythm",
        "unit": "seconds",
        "expected_range": [0.0, 3600.0],
        "dependency": []
    },
    {
        "name": "rhythm_speech_rate",
        "group": "Rhythm",
        "unit": "bpm",
        "expected_range": [0.0, 300.0],
        "dependency": []
    },
    {
        "name": "rhythm_pause_count",
        "group": "Rhythm",
        "unit": "count",
        "expected_range": [0, 1000],
        "dependency": []
    },
    {
        "name": "rhythm_mean_pause_duration",
        "group": "Rhythm",
        "unit": "seconds",
        "expected_range": [0.0, 10.0],
        "dependency": ["rhythm_pause_count"]
    },
    {
        "name": "spectral_centroid_mean",
        "group": "Spectral",
        "unit": "Hz",
        "expected_range": [0.0, 12000.0],
        "dependency": []
    },
    {
        "name": "spectral_rolloff_mean",
        "group": "Spectral",
        "unit": "Hz",
        "expected_range": [0.0, 12000.0],
        "dependency": []
    },
    {
        "name": "spectral_bandwidth_mean",
        "group": "Spectral",
        "unit": "Hz",
        "expected_range": [0.0, 12000.0],
        "dependency": []
    },
    {
        "name": "spectral_contrast_mean",
        "group": "Spectral",
        "unit": "dB",
        "expected_range": [0.0, 100.0],
        "dependency": []
    },
    {
        "name": "vq_zero_crossing_rate",
        "group": "Voice Quality",
        "unit": "ratio",
        "expected_range": [0.0, 1.0],
        "dependency": []
    },
    {
        "name": "vq_spectral_flatness",
        "group": "Voice Quality",
        "unit": "ratio",
        "expected_range": [0.0, 1.0],
        "dependency": []
    },
    {
        "name": "vq_harmonic_ratio",
        "group": "Voice Quality",
        "unit": "ratio",
        "expected_range": [0.0, 1.0],
        "dependency": []
    }
]

# Provide the original ordered string list to maintain backward compatibility for internal functions
FEATURE_REGISTRY = [feature["name"] for feature in FEATURE_REGISTRY_METADATA]

# The fixed dimension N of the feature vector
FEATURE_DIMENSION = len(FEATURE_REGISTRY)
