"""
feature_graph.py
Static mapping from acoustic features to candidate levers.

Each feature maps to one or more levers that have been identified (via Stage 2
source-code inspection) as potential influencers of that feature.

This module describes relationships ONLY.
It does NOT score, rank, recommend, or optimize.
"""

# Structure:
# FEATURE_GRAPH[feature_name] = [
#     {
#         "lever":              str (key in LEVER_DATABASE),
#         "relationship_type":  str ("DIRECT" | "INDIRECT" | "COUPLED"),
#         "evidence":           str
#     }, ...
# ]

FEATURE_GRAPH = {

    # -------------------------------------------------------------------------
    # PITCH
    # -------------------------------------------------------------------------
    "pitch_f0_mean": [
        {
            "lever":             "cfg_strength",
            "relationship_type": "DIRECT",
            "evidence":          "CFG amplifies adherence to reference conditioning, which encodes F0 contour."
        }
    ],
    "pitch_f0_variance": [
        {
            "lever":             "cfg_strength",
            "relationship_type": "DIRECT",
            "evidence":          "Higher CFG forces tighter adherence; lower CFG allows more F0 drift."
        }
    ],
    "pitch_voiced_ratio": [
        {
            "lever":             "cfg_strength",
            "relationship_type": "INDIRECT",
            "evidence":          "CFG indirectly determines how well voiced/unvoiced regions are preserved."
        },
        {
            "lever":             "edit_mask",
            "relationship_type": "DIRECT",
            "evidence":          "Masking voiced frames forces model to regenerate only unvoiced regions."
        }
    ],

    # -------------------------------------------------------------------------
    # ENERGY
    # -------------------------------------------------------------------------
    "energy_rms_mean": [
        {
            "lever":             "target_rms",
            "relationship_type": "DIRECT",
            "evidence":          "target_rms scales audio amplitude before and after generation."
        },
        {
            "lever":             "cfg_strength",
            "relationship_type": "INDIRECT",
            "evidence":          "CFG adherence to reference audio also captures its energy envelope."
        }
    ],
    "energy_rms_variance": [
        {
            "lever":             "cfg_strength",
            "relationship_type": "INDIRECT",
            "evidence":          "CFG affects how dynamically the energy varies across time."
        }
    ],
    "energy_peak": [
        {
            "lever":             "target_rms",
            "relationship_type": "DIRECT",
            "evidence":          "Peak amplitude is directly scaled by target_rms normalization."
        }
    ],
    "energy_crest_factor": [
        {
            "lever":             "target_rms",
            "relationship_type": "COUPLED",
            "evidence":          "Crest factor = peak / rms. Both are scaled by target_rms, but ratio may shift."
        }
    ],

    # -------------------------------------------------------------------------
    # RHYTHM
    # -------------------------------------------------------------------------
    "rhythm_speech_duration": [
        {
            "lever":             "speed",
            "relationship_type": "DIRECT",
            "evidence":          "speed divides the character-proportional duration estimate linearly."
        }
    ],
    "rhythm_silence_duration": [
        {
            "lever":             "speed",
            "relationship_type": "DIRECT",
            "evidence":          "Total duration changes with speed; silence is derived from total minus speech."
        },
        {
            "lever":             "cross_fade_duration",
            "relationship_type": "INDIRECT",
            "evidence":          "Cross-fade merges chunk boundaries, potentially eliminating inter-chunk silences."
        }
    ],
    "rhythm_speech_rate": [
        {
            "lever":             "speed",
            "relationship_type": "DIRECT",
            "evidence":          "Speech rate is inversely proportional to output duration."
        }
    ],
    "rhythm_pause_count": [
        {
            "lever":             "cross_fade_duration",
            "relationship_type": "INDIRECT",
            "evidence":          "Longer cross-fade can merge pauses at chunk boundaries."
        }
    ],
    "rhythm_mean_pause_duration": [
        {
            "lever":             "speed",
            "relationship_type": "INDIRECT",
            "evidence":          "Pause durations are affected by total duration scaling."
        },
        {
            "lever":             "cross_fade_duration",
            "relationship_type": "INDIRECT",
            "evidence":          "Cross-fade duration physically overlaps silence regions."
        }
    ],

    # -------------------------------------------------------------------------
    # SPECTRAL
    # -------------------------------------------------------------------------
    "spectral_centroid_mean": [
        {
            "lever":             "cfg_strength",
            "relationship_type": "INDIRECT",
            "evidence":          "CFG conditioning adherence shapes spectral envelope of output."
        },
        {
            "lever":             "sway_sampling_coef",
            "relationship_type": "INDIRECT",
            "evidence":          "Timestep warping changes which frequency components emerge first in integration."
        }
    ],
    "spectral_rolloff_mean": [
        {
            "lever":             "cfg_strength",
            "relationship_type": "INDIRECT",
            "evidence":          "CFG constrains frequency rolloff toward reference."
        },
        {
            "lever":             "sway_sampling_coef",
            "relationship_type": "INDIRECT",
            "evidence":          "Sway sampling affects high-frequency integration fidelity."
        }
    ],
    "spectral_bandwidth_mean": [
        {
            "lever":             "cfg_strength",
            "relationship_type": "INDIRECT",
            "evidence":          "CFG narrows bandwidth toward reference when strength is high."
        },
        {
            "lever":             "sway_sampling_coef",
            "relationship_type": "INDIRECT",
            "evidence":          "Timestep concentration affects spectral band resolution."
        }
    ],
    "spectral_contrast_mean": [
        {
            "lever":             "cfg_strength",
            "relationship_type": "INDIRECT",
            "evidence":          "High CFG preserves harmonic-noise contrast from reference conditioning."
        }
    ],

    # -------------------------------------------------------------------------
    # VOICE QUALITY
    # -------------------------------------------------------------------------
    "vq_zero_crossing_rate": [
        {
            "lever":             "nfe_step",
            "relationship_type": "INDIRECT",
            "evidence":          "Higher NFE reduces high-frequency noise artifacts that drive ZCR up."
        },
        {
            "lever":             "sway_sampling_coef",
            "relationship_type": "INDIRECT",
            "evidence":          "Sway warping affects integration smoothness in high-frequency bands."
        }
    ],
    "vq_spectral_flatness": [
        {
            "lever":             "nfe_step",
            "relationship_type": "INDIRECT",
            "evidence":          "More steps yields a less noisy (less flat) spectrogram."
        },
        {
            "lever":             "sway_sampling_coef",
            "relationship_type": "INDIRECT",
            "evidence":          "Timestep distribution shapes noise floor."
        }
    ],
    "vq_harmonic_ratio": [
        {
            "lever":             "nfe_step",
            "relationship_type": "INDIRECT",
            "evidence":          "Step count directly affects harmonic reconstruction fidelity."
        },
        {
            "lever":             "cfg_strength",
            "relationship_type": "COUPLED",
            "evidence":          "Extreme CFG can introduce artifacts that depress harmonic ratio."
        }
    ]
}
