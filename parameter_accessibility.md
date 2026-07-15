# F5-TTS KNOWLEDGE BASE: PARAMETER ACCESSIBILITY

This document classifies every discovered lever based on how easily an external controller can manipulate it without modifying the core F5-TTS source code.

## 1. API Accessible
*These levers can be passed directly as arguments to `infer_process` or `CFM.sample`. They are ready for AI Controller integration.*
- `speed` (PRE-001)
- `target_rms` (PRE-002)
- `cross_fade_duration` (PRE-003)
- `nfe_step` / `steps` (CFM-001)
- `cfg_strength` (CFM-002)
- `sway_sampling_coef` (CFM-003)
- `edit_mask` (CFM-004)

## 2. Configuration Accessible
*These levers are defined in config dictionaries when initializing the model, requiring model re-instantiation to change.*
- `ode_method` (e.g., euler vs midpoint)
- `mel_spec_type` (vocos vs bigvgan)

## 3. Source Modification Required
*These levers require altering the source code to intercept or modify their behavior.*
- `frac_lengths_mask` (CFM initiation, used primarily for training but hardcoded defaults exist)
- Pitch scaling multiplier (Currently doesn't exist; would require injecting `cond * factor` inside CFM)

## 4. Internal Only
*These are mathematical routing flags used internally by the network. Exposing them breaks the architecture.*
- `drop_audio_cond` (DIT-001)
- `drop_text` (DIT-002)
- `Rotary Position Embedding / rope`
