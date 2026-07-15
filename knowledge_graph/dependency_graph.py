"""
dependency_graph.py
Static lever-to-lever dependency map.

Documents which levers constrain, enable, or are entangled with other levers.

This module describes structural dependencies ONLY.
It does NOT perform inference, optimization, or parameter recommendation.
"""

# Relationship types:
#   REQUIRES   : Lever A will only function if Lever B is also active
#   CONSTRAINS : Lever A limits the effective range of Lever B
#   ENTANGLED  : Changing Lever A produces inseparable side-effects on Lever B

DEPENDENCY_GRAPH = {

    "cfg_strength": [
        {
            "depends_on":        "drop_audio_cond",
            "relationship":      "REQUIRES",
            "direction":         "cfg_strength -> drop_audio_cond",
            "description":       (
                "cfg_strength > 0 triggers a dual forward pass inside CFM.sample. "
                "The null (unconditioned) prediction uses drop_audio_cond=True internally. "
                "cfg_strength cannot function without this routing."
            )
        }
    ],

    "sway_sampling_coef": [
        {
            "depends_on":        "nfe_step",
            "relationship":      "CONSTRAINS",
            "direction":         "nfe_step -> sway_sampling_coef",
            "description":       (
                "The effectiveness of sway sampling depends on the total number of timesteps. "
                "With very few steps (< 8), the cosine warp collapses too many steps into a "
                "single region, negating its intended benefit."
            )
        }
    ],

    "edit_mask": [
        {
            "depends_on":        "cfg_strength",
            "relationship":      "ENTANGLED",
            "direction":         "edit_mask <-> cfg_strength",
            "description":       (
                "When edit_mask is active, cond_mask combines with it before the CFG dual forward. "
                "The cfg_strength then applies only to the unmasked (to-be-generated) frames. "
                "The two levers jointly determine the generation boundary."
            )
        }
    ],

    "speed": [],               # No upstream lever dependencies
    "target_rms": [],          # No upstream lever dependencies
    "cross_fade_duration": [], # No upstream lever dependencies; downstream only
    "nfe_step": [],            # Upstream constrainer; no dependency itself
    "drop_audio_cond": []      # Internal-only; listed for completeness
}
