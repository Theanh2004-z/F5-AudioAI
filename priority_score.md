# F5-TTS KNOWLEDGE BASE: PRIORITY SCORE

This document ranks every lever using the formula:
**Priority = Accessibility × Isolation × Expected Gain × Safety**
(Scoring scale for each factor is 1 to 5).

| Lever | Accessibility | Isolation | Expected Gain | Safety | Priority Score |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **`speed`** (PRE-001) | 5 | 5 | 4 | 5 | **500** |
| **`target_rms`** (PRE-002) | 5 | 5 | 4 | 5 | **500** |
| **`edit_mask`** (CFM-004) | 5 | 5 | 4 | 4 | **400** |
| **`cross_fade_duration`** (PRE-003) | 5 | 4 | 3 | 4 | **240** |
| **`cfg_strength`** (CFM-002) | 5 | 2 | 5 | 3 | **150** |
| **`steps / nfe_step`** (CFM-001) | 5 | 2 | 2 | 5 | **100** |
| **`sway_sampling_coef`** (CFM-003)| 5 | 1 | 3 | 2 | **30** |
| **`drop_audio_cond`** (DIT-001) | 1 | 1 | 1 | 1 | **1** |

### Factor Definitions:
- **Accessibility:** 5 = API accessible, 1 = Internal code mod required.
- **Isolation:** 5 = Changes exactly one acoustic feature. 1 = Changes everything chaotically.
- **Expected Gain:** 5 = Immense influence on the final emotional performance. 1 = Negligible visual/audible difference.
- **Safety:** 5 = Impossible to crash/distort. 1 = High likelihood of generating robotic noise or tensor shape errors.
