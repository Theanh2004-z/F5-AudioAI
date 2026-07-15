# Registry defining every tunable parameter separately for future AI Controller
# NO tuning logic. Registry only.

PARAMETER_REGISTRY = [
    {
        "name": "f0_scale",
        "description": "Scales the F0 contour up or down to modify pitch mean.",
        "default_value": 1.0,
        "min": 0.5,
        "max": 2.0,
        "data_type": "float",
        "affected_feature_groups": ["Pitch"],
        "confidence": 1.0
    },
    {
        "name": "energy_multiplier",
        "description": "Multiplies RMS amplitude to adjust overall loudness.",
        "default_value": 1.0,
        "min": 0.1,
        "max": 5.0,
        "data_type": "float",
        "affected_feature_groups": ["Energy"],
        "confidence": 1.0
    },
    {
        "name": "speed_ratio",
        "description": "Modifies the generation speed impacting duration and speech rate.",
        "default_value": 1.0,
        "min": 0.5,
        "max": 2.0,
        "data_type": "float",
        "affected_feature_groups": ["Rhythm"],
        "confidence": 0.9
    },
    {
        "name": "pause_duration_scale",
        "description": "Scales the duration of silence segments.",
        "default_value": 1.0,
        "min": 0.0,
        "max": 3.0,
        "data_type": "float",
        "affected_feature_groups": ["Rhythm"],
        "confidence": 0.8
    }
]

def get_parameter_registry():
    return PARAMETER_REGISTRY
