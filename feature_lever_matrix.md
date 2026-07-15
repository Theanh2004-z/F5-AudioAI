# F5-TTS KNOWLEDGE BASE: FEATURE-LEVER MATRIX

This matrix provides a reverse mapping from target acoustic features back to the candidate levers that can manipulate them.

| Target Feature Group | Specific Metric | Candidate Levers |
| :--- | :--- | :--- |
| **Pitch** | f0_mean | `cfg_strength` |
| | f0_variance | `cfg_strength` |
| | voiced_ratio | `cfg_strength`, `edit_mask` |
| **Energy** | rms_mean | `target_rms`, `cfg_strength` |
| | rms_variance | `target_rms`, `cfg_strength` |
| | peak | `target_rms` |
| | crest_factor | `target_rms`, `cfg_strength` |
| **Rhythm** | speech_duration | `speed` |
| | silence_duration | `speed`, `cross_fade_duration` |
| | speech_rate | `speed` |
| | pause_count | `cross_fade_duration` |
| | mean_pause_duration | `speed`, `cross_fade_duration` |
| **Spectral** | centroid_mean | `cfg_strength`, `sway_sampling_coef` |
| | rolloff_mean | `cfg_strength`, `sway_sampling_coef` |
| | bandwidth_mean | `cfg_strength`, `sway_sampling_coef` |
| | contrast_mean | `cfg_strength`, `sway_sampling_coef` |
| **Voice Quality** | zero_crossing_rate | `steps` (nfe_step), `sway_sampling_coef` |
| | spectral_flatness | `steps` (nfe_step), `sway_sampling_coef` |
| | harmonic_ratio | `steps` (nfe_step), `sway_sampling_coef` |
