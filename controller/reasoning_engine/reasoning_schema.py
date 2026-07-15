"""
reasoning_schema.py
Schema constants, version metadata, and field documentation
for the Reasoning Engine output.

No optimization. No tuning. No parameter recommendation.
"""

REASONING_ENGINE_VERSION = "1.0.0"

# ── Classification scores used for confidence fusion ──────────────────────────
# These are static weights assigned to observation quality labels.
# They represent how trustworthy a given observation is as evidence.
# NOT thresholds for parameter tuning.
OBSERVATION_QUALITY_WEIGHT = {
    "VALID":           1.00,
    "LOW_CONFIDENCE":  0.60,
    "OUT_OF_RANGE":    0.50,
    "SUSPECT":         0.40,
    "INVALID":         0.10,
    "MISSING":         0.00
}

# Static weights for each graph relationship type as evidence quality.
# DIRECT edges are stronger evidence than INDIRECT ones.
RELATIONSHIP_TYPE_WEIGHT = {
    "DIRECT":   1.00,
    "COUPLED":  0.85,
    "INDIRECT": 0.65
}

# Reasoning confidence threshold below which a hypothesis is considered "WEAK"
# and should be placed in warnings rather than candidate_hypotheses.
# This does NOT tune any parameter. It only filters the report content.
WEAK_HYPOTHESIS_THRESHOLD = 0.30

# ── Output schema field documentation ────────────────────────────────────────
OUTPUT_SCHEMA_DOC = {
    "metadata": {
        "version":   "Reasoning Engine version string.",
        "timestamp": "ISO-like timestamp of report generation."
    },
    "feature_observations": [
        {
            "feature":                "Feature name from FEATURE_REGISTRY.",
            "group":                  "Feature group (Pitch/Energy/Rhythm/Spectral/Voice Quality).",
            "normalized_difference":  "Normalized diff value from normalized_feature_difference.json. Range [-1,1].",
            "observation_quality":    "Quality label from observation_report.json.",
            "ref_confidence":         "Reference audio measurement confidence [0,1].",
            "gen_confidence":         "Generated audio measurement confidence [0,1].",
            "observation_strength":   "Derived weight = |normalized_difference| x min(ref_conf, gen_conf)."
        }
    ],
    "candidate_hypotheses": [
        {
            "feature":                "The observed acoustic feature.",
            "candidate_lever":        "Lever name from knowledge_graph.json. NOT a parameter value.",
            "relationship_type":      "DIRECT | INDIRECT | COUPLED — from knowledge graph edge.",
            "supporting_evidence":    "List of human-readable evidence strings aggregated from all sources.",
            "reasoning_confidence":   "Fused confidence [0,1] — reflects evidence quality, NOT a tuning signal."
        }
    ],
    "unknowns": [
        {
            "feature":  "Feature with a non-trivial observation but NO graph edge to any lever.",
            "reason":   "Why this feature could not be explained."
        }
    ],
    "warnings": [
        "Human-readable warning strings about low-confidence observations, missing data, etc."
    ]
}
