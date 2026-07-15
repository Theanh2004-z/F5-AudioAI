# F5-TTS KNOWLEDGE BASE: LEVER PROFILES

This document profiles every identified lever in the F5-TTS inference pipeline, providing structural, functional, and behavioral metadata.

---

## 1. PRE-001: Speed Ratio
- **File:** `src/f5_tts/infer/utils_infer.py`
- **Class:** `None`
- **Function:** `infer_batch_process`
- **Variable:** `speed`
- **Input:** Float (e.g., 0.5 to 2.0)
- **Output:** Int (Frame duration for ODE solver)
- **Feature Groups Affected:** Rhythm (Speech Rate, Speech Duration, Pause Duration)
- **Expected Influence Strength:** High
- **Coupling Level:** Low (Independent variable)
- **Linearity:** Linear (1.0 = normal, 2.0 = half length)
- **Accessibility:** API Accessible (Passed as arg)
- **Risk:** Low
- **Confidence:** 0.95

## 2. PRE-002: Target RMS
- **File:** `src/f5_tts/infer/utils_infer.py`
- **Class:** `None`
- **Function:** `infer_batch_process`
- **Variable:** `target_rms`
- **Input:** Float (e.g., 0.1)
- **Output:** Tensor (Amplitude scaled)
- **Feature Groups Affected:** Energy (RMS Mean, Peak)
- **Expected Influence Strength:** High
- **Coupling Level:** Low
- **Linearity:** Linear
- **Accessibility:** API Accessible
- **Risk:** Low
- **Confidence:** 0.95

## 3. PRE-003: Cross-fade Duration
- **File:** `src/f5_tts/infer/utils_infer.py`
- **Class:** `None`
- **Function:** `infer_batch_process`
- **Variable:** `cross_fade_duration`
- **Input:** Float (Seconds, e.g., 0.15)
- **Output:** Numpy Array (Faded overlapping audio)
- **Feature Groups Affected:** Rhythm (Pause Duration), Spectral (Continuity)
- **Expected Influence Strength:** Medium
- **Coupling Level:** Medium (Depends on batch chunking)
- **Linearity:** Non-Linear (Phase interference)
- **Accessibility:** API Accessible
- **Risk:** Medium
- **Confidence:** 0.85

## 4. CFM-001: ODE Integration Steps
- **File:** `src/f5_tts/model/cfm.py`
- **Class:** `CFM`
- **Function:** `sample`
- **Variable:** `steps` (nfe_step)
- **Input:** Int (e.g., 16, 32)
- **Output:** Tensor (Trajectory depth)
- **Feature Groups Affected:** Voice Quality (HNR, ZCR)
- **Expected Influence Strength:** Low (Mostly compute trade-off)
- **Coupling Level:** High (Coupled with solver method)
- **Linearity:** Asymptotic (Plateaus after ~32)
- **Accessibility:** API Accessible
- **Risk:** Low
- **Confidence:** 0.99

## 5. CFM-002: CFG Strength
- **File:** `src/f5_tts/model/cfm.py`
- **Class:** `CFM`
- **Function:** `sample`
- **Variable:** `cfg_strength`
- **Input:** Float (e.g., 2.0)
- **Output:** Tensor (Vector field extrapolation)
- **Feature Groups Affected:** Pitch, Energy, Timbre
- **Expected Influence Strength:** Extreme
- **Coupling Level:** High (Coupled with Null prediction)
- **Linearity:** Non-Linear (Values > 3 cause catastrophic failure)
- **Accessibility:** API Accessible
- **Risk:** High
- **Confidence:** 0.70

## 6. CFM-003: Sway Sampling Coefficient
- **File:** `src/f5_tts/model/cfm.py`
- **Class:** `CFM`
- **Function:** `sample`
- **Variable:** `sway_sampling_coef`
- **Input:** Float (e.g., -1.0)
- **Output:** Tensor (Time step warping)
- **Feature Groups Affected:** Voice Quality (Spectral Flatness)
- **Expected Influence Strength:** Medium
- **Coupling Level:** High
- **Linearity:** Non-Linear (Cosine transformation)
- **Accessibility:** API Accessible
- **Risk:** High
- **Confidence:** 0.60

## 7. CFM-004: Edit Masking
- **File:** `src/f5_tts/model/cfm.py`
- **Class:** `CFM`
- **Function:** `sample`
- **Variable:** `edit_mask`
- **Input:** Boolean Tensor
- **Output:** Tensor (Masked conditioning)
- **Feature Groups Affected:** Timbre, Rhythm
- **Expected Influence Strength:** High
- **Coupling Level:** Low
- **Linearity:** Binary (1 or 0 replacement)
- **Accessibility:** API Accessible
- **Risk:** Medium
- **Confidence:** 0.80

## 8. DIT-001: Text / Audio Cond Dropout
- **File:** `src/f5_tts/model/backbones/dit.py`
- **Class:** `DiT`
- **Function:** `forward`
- **Variable:** `drop_audio_cond`, `drop_text`
- **Input:** Boolean
- **Output:** Tensor (Zeroed embeddings)
- **Feature Groups Affected:** All
- **Expected Influence Strength:** Extreme
- **Coupling Level:** High (Used by CFM-002)
- **Linearity:** N/A
- **Accessibility:** Internal Only
- **Risk:** Extreme
- **Confidence:** 1.0
