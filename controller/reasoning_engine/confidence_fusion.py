"""
confidence_fusion.py
Fuses multiple independent evidence signals into a single reasoning_confidence
score in [0, 1].

This score reflects "how trustworthy is the hypothesis that this lever
is related to what we observed?" — NOT a tuning signal.

Fusion formula (deterministic, no ML):

  reasoning_confidence =
      observation_quality_weight(gen_quality)       [0,1]
    × min(ref_confidence, gen_confidence)            [0,1]
    × relationship_type_weight(relationship_type)    [0,1]
    × clamp(observation_strength × amplifier, 0, 1) [0,1]

All weights are static constants from reasoning_schema.py.
No optimization. No parameter recommendation.
"""

from reasoning_schema import (
    OBSERVATION_QUALITY_WEIGHT,
    RELATIONSHIP_TYPE_WEIGHT
)

# Amplification factor for observation_strength so that small but non-zero
# differences still contribute meaningfully.
# This is purely a display/legibility choice — NOT a tuning threshold.
STRENGTH_AMPLIFIER = 3.0


def fuse_confidence(
    gen_quality,
    ref_confidence,
    gen_confidence,
    relationship_type,
    observation_strength
):
    """
    Computes a single reasoning_confidence score from 4 independent signals.

    Args:
        gen_quality          : str   — quality label of the generated feature
        ref_confidence       : float — measurement confidence for reference [0,1]
        gen_confidence       : float — measurement confidence for generated [0,1]
        relationship_type    : str   — "DIRECT" | "INDIRECT" | "COUPLED"
        observation_strength : float — |normalized_diff| × min(conf) ≥ 0

    Returns:
        float — reasoning_confidence in [0, 1], rounded to 4 decimals
    """
    q_weight  = OBSERVATION_QUALITY_WEIGHT.get(gen_quality, 0.0)
    r_weight  = RELATIONSHIP_TYPE_WEIGHT.get(relationship_type, 0.5)
    conf_min  = min(ref_confidence, gen_confidence)
    strength  = min(1.0, observation_strength * STRENGTH_AMPLIFIER)

    fused = q_weight * conf_min * r_weight * strength
    return round(max(0.0, min(1.0, fused)), 4)
