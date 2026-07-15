"""
lever_database.py
Static database of every discovered intervention lever in the F5-TTS pipeline.

Each lever record describes structural and behavioral properties.
This module contains NO recommendation logic, NO scoring, NO optimization.
It is a read-only catalog of facts derived from source code inspection (Stage 2).
"""

# Accessibility classifications
ACCESS_API         = "API_ACCESSIBLE"       # Passable as argument to infer_process / CFM.sample
ACCESS_CONFIG      = "CONFIG_ACCESSIBLE"    # Set at model instantiation, requires re-init
ACCESS_SOURCE      = "SOURCE_MOD_REQUIRED"  # Requires altering F5 source code
ACCESS_INTERNAL    = "INTERNAL_ONLY"        # Mathematical routing flag, must not be exposed

# Evidence source classifications
EVIDENCE_CODE      = "SOURCE_CODE_INSPECTION"
EVIDENCE_PAPER     = "PAPER_REFERENCE"
EVIDENCE_EMPIRICAL = "EMPIRICAL_OBSERVATION"


LEVER_DATABASE = {

    "speed": {
        "lever_id":          "PRE-001",
        "name":              "speed",
        "file":              "src/f5_tts/infer/utils_infer.py",
        "class":             None,
        "function":          "infer_batch_process",
        "variable":          "speed",
        "accessibility":     ACCESS_API,
        "coupling":          "LOW",      # Changes only duration estimation; isolated from DiT
        "linearity":         "LINEAR",   # duration scales linearly with 1/speed
        "safety":            "HIGH",     # No risk of NaN or artifact within [0.5, 2.0]
        "expected_influence": {
            "Rhythm":  "HIGH",
            "Pitch":   "NONE",
            "Energy":  "NONE",
            "Spectral":"NONE",
            "Voice Quality": "NONE"
        },
        "evidence_source":   EVIDENCE_CODE,
        "notes":             "Controls the integer frame count passed to CFM.sample as `duration`."
    },

    "target_rms": {
        "lever_id":          "PRE-002",
        "name":              "target_rms",
        "file":              "src/f5_tts/infer/utils_infer.py",
        "class":             None,
        "function":          "infer_batch_process",
        "variable":          "target_rms",
        "accessibility":     ACCESS_API,
        "coupling":          "LOW",
        "linearity":         "LINEAR",
        "safety":            "HIGH",
        "expected_influence": {
            "Energy":  "HIGH",
            "Pitch":   "NONE",
            "Rhythm":  "NONE",
            "Spectral":"NONE",
            "Voice Quality": "NONE"
        },
        "evidence_source":   EVIDENCE_CODE,
        "notes":             "Applied pre-inference (ref audio scaling) and post-inference (inverse scaling of output)."
    },

    "cross_fade_duration": {
        "lever_id":          "PRE-003",
        "name":              "cross_fade_duration",
        "file":              "src/f5_tts/infer/utils_infer.py",
        "class":             None,
        "function":          "infer_batch_process",
        "variable":          "cross_fade_duration",
        "accessibility":     ACCESS_API,
        "coupling":          "MEDIUM",
        "linearity":         "NON_LINEAR",  # Phase interference between overlapping chunks
        "safety":            "HIGH",
        "expected_influence": {
            "Rhythm":  "MEDIUM",
            "Spectral":"LOW",
            "Pitch":   "NONE",
            "Energy":  "NONE",
            "Voice Quality": "NONE"
        },
        "evidence_source":   EVIDENCE_CODE,
        "notes":             "Only active when multi-chunk batching occurs (long text)."
    },

    "nfe_step": {
        "lever_id":          "CFM-001",
        "name":              "nfe_step",
        "file":              "src/f5_tts/model/cfm.py",
        "class":             "CFM",
        "function":          "sample",
        "variable":          "steps",
        "accessibility":     ACCESS_API,
        "coupling":          "HIGH",        # Coupled with ODE method (euler/midpoint)
        "linearity":         "ASYMPTOTIC",  # Quality plateaus after ~32 steps
        "safety":            "HIGH",
        "expected_influence": {
            "Voice Quality": "MEDIUM",
            "Spectral":      "LOW",
            "Pitch":         "NONE",
            "Energy":        "NONE",
            "Rhythm":        "NONE"
        },
        "evidence_source":   EVIDENCE_CODE,
        "notes":             "Pure compute-quality trade-off. Not a stylistic parameter."
    },

    "cfg_strength": {
        "lever_id":          "CFM-002",
        "name":              "cfg_strength",
        "file":              "src/f5_tts/model/cfm.py",
        "class":             "CFM",
        "function":          "sample",
        "variable":          "cfg_strength",
        "accessibility":     ACCESS_API,
        "coupling":          "HIGH",        # Affects Pitch, Energy, Timbre simultaneously
        "linearity":         "NON_LINEAR",  # Catastrophic failure above ~3.5
        "safety":            "MEDIUM",
        "expected_influence": {
            "Pitch":         "HIGH",
            "Energy":        "HIGH",
            "Voice Quality": "MEDIUM",
            "Spectral":      "MEDIUM",
            "Rhythm":        "LOW"
        },
        "evidence_source":   EVIDENCE_CODE,
        "notes":             "Extrapolates: pred + (pred - null_pred) * cfg_strength. High coupling to drop_audio_cond."
    },

    "sway_sampling_coef": {
        "lever_id":          "CFM-003",
        "name":              "sway_sampling_coef",
        "file":              "src/f5_tts/model/cfm.py",
        "class":             "CFM",
        "function":          "sample",
        "variable":          "sway_sampling_coef",
        "accessibility":     ACCESS_API,
        "coupling":          "HIGH",
        "linearity":         "NON_LINEAR",  # Cosine-warped time schedule
        "safety":            "LOW",
        "expected_influence": {
            "Voice Quality": "MEDIUM",
            "Spectral":      "MEDIUM",
            "Pitch":         "LOW",
            "Energy":        "LOW",
            "Rhythm":        "NONE"
        },
        "evidence_source":   EVIDENCE_CODE,
        "notes":             "Warps timestep distribution: t = t + coef*(cos(pi/2*t) - 1 + t)."
    },

    "edit_mask": {
        "lever_id":          "CFM-004",
        "name":              "edit_mask",
        "file":              "src/f5_tts/model/cfm.py",
        "class":             "CFM",
        "function":          "sample",
        "variable":          "edit_mask",
        "accessibility":     ACCESS_API,
        "coupling":          "LOW",
        "linearity":         "BINARY",   # Either a frame is regenerated or not
        "safety":            "MEDIUM",
        "expected_influence": {
            "Rhythm":        "HIGH",
            "Pitch":         "MEDIUM",
            "Energy":        "MEDIUM",
            "Voice Quality": "MEDIUM",
            "Spectral":      "MEDIUM"
        },
        "evidence_source":   EVIDENCE_CODE,
        "notes":             "Requires external VAD/segmentation to generate the boolean mask tensor."
    },

    "drop_audio_cond": {
        "lever_id":          "DIT-001",
        "name":              "drop_audio_cond",
        "file":              "src/f5_tts/model/backbones/dit.py",
        "class":             "DiT",
        "function":          "forward",
        "variable":          "drop_audio_cond",
        "accessibility":     ACCESS_INTERNAL,
        "coupling":          "EXTREME",
        "linearity":         "BINARY",
        "safety":            "EXTREME_RISK",
        "expected_influence": {
            "Pitch":         "EXTREME",
            "Energy":        "EXTREME",
            "Voice Quality": "EXTREME",
            "Spectral":      "EXTREME",
            "Rhythm":        "EXTREME"
        },
        "evidence_source":   EVIDENCE_CODE,
        "notes":             "Routing flag for CFG null branch. Zeroes conditioning tensor. Must not be exposed."
    }
}
