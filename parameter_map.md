# F5-TTS INFERENCE PIPELINE: PARAMETER MAP
*(Reverse Engineering Document - No Optimization)*

## OVERVIEW
This document catalogs every tunable intervention point ("Lever") within the F5-TTS inference pipeline, spanning from text chunking and audio prep (`utils_infer.py`) down to the core Diffusion Transformer and Conditional Flow Matching ODE solver (`dit.py`, `cfm.py`).

---

## 1. PRE-PROCESSING & BATCHING LEVERS

### Lever ID: PRE-001 (Speed Ratio)
- **File:** `src/f5_tts/infer/utils_infer.py`
- **Function:** `infer_batch_process`
- **Variable:** `speed` (also overridden by `local_speed`)
- **Purpose:** Controls the explicit temporal length of the generated spectrogram by scaling the proportional character-to-audio duration estimation.
- **Input:** Float (default: 1.0)
- **Output:** Integer (frames of generation duration)
- **Related Feature Groups:** Rhythm (Speech Rate, Speech Duration)
- **Expected Influence:** Directly expands or shrinks the generated time axis linearly.
- **Risk Level:** LOW
- **Dependency:** `ref_text`, `gen_text`, `ref_audio_len`

### Lever ID: PRE-002 (Target RMS Normalization)
- **File:** `src/f5_tts/infer/utils_infer.py`
- **Function:** `infer_batch_process`
- **Variable:** `target_rms`
- **Purpose:** Normalizes the input reference audio volume to a minimum RMS threshold before condition extraction, and inversely applies it post-generation.
- **Input:** Float (default: 0.1)
- **Output:** Float tensor (amplitude scaled)
- **Related Feature Groups:** Energy (RMS Mean, Peak)
- **Expected Influence:** Shifts the global loudness of the output. Does not affect variance/dynamics natively.
- **Risk Level:** LOW
- **Dependency:** None

### Lever ID: PRE-003 (Cross-fade Duration)
- **File:** `src/f5_tts/infer/utils_infer.py`
- **Function:** `infer_batch_process`
- **Variable:** `cross_fade_duration`
- **Purpose:** Dictates the overlap mixing window when concatenating multiple generated text chunks.
- **Input:** Float (seconds, default: 0.15)
- **Output:** Numpy array (faded overlap)
- **Related Feature Groups:** Rhythm (Pause Duration), Spectral (Transitions)
- **Expected Influence:** Modifies the spacing (pause) and spectral continuity between synthesized sentences.
- **Risk Level:** MEDIUM (Too low = harsh cuts; Too high = overlapping speech/mumbling)
- **Dependency:** Batching logic

---

## 2. CONDITIONAL FLOW MATCHING (CFM) LEVERS

### Lever ID: CFM-001 (ODE Solver Steps / NFE)
- **File:** `src/f5_tts/model/cfm.py`
- **Function:** `CFM.sample`
- **Variable:** `steps` (mapped from `nfe_step`)
- **Purpose:** Determines the number of integration steps the ODE solver uses to map Gaussian noise to the target Mel spectrogram.
- **Input:** Integer (default: 32)
- **Output:** Trajectory tensor
- **Related Feature Groups:** Voice Quality (Harmonic Ratio, Zero Crossing), Spectral
- **Expected Influence:** Higher steps yield smoother, less noisy spectral envelopes at the cost of RTF (Real-Time Factor).
- **Risk Level:** LOW (Safe, trades compute for quality)
- **Dependency:** ODE Method (`euler`, `midpoint`)

### Lever ID: CFM-002 (Classifier-Free Guidance Strength)
- **File:** `src/f5_tts/model/cfm.py`
- **Function:** `CFM.sample`
- **Variable:** `cfg_strength`
- **Purpose:** Amplifies the conditional vector field direction over the unconditional one. `pred + (pred - null_pred) * cfg_strength`
- **Input:** Float (default: 2.0)
- **Output:** Extrapolated flow prediction tensor
- **Related Feature Groups:** Pitch (F0 Variance), Energy (Variance), Timbre
- **Expected Influence:** Highly impacts expressiveness and speaker adherence. High values force the model to aggressively follow the reference's performance.
- **Risk Level:** HIGH (Excessive CFG > 3.0 usually causes severe audio artifacts, screeching, or distortion).
- **Dependency:** Requires `drop_audio_cond` routing in the DiT block.

### Lever ID: CFM-003 (Sway Sampling Coefficient)
- **File:** `src/f5_tts/model/cfm.py`
- **Function:** `CFM.sample`
- **Variable:** `sway_sampling_coef`
- **Purpose:** Non-linearly warps the linear time schedule `t` during ODE integration to focus computational steps on specific difficulty regions of the diffusion process.
- **Input:** Float (default: -1.0)
- **Output:** Modified time schedule tensor `t`
- **Related Feature Groups:** Voice Quality (Spectral Flatness), Timbre
- **Expected Influence:** Affects the crispness of high frequencies and stability of phoneme transitions. 
- **Risk Level:** MEDIUM
- **Dependency:** `use_epss`

### Lever ID: CFM-004 (Edit Masking)
- **File:** `src/f5_tts/model/cfm.py`
- **Function:** `CFM.sample`
- **Variable:** `edit_mask`
- **Purpose:** Forces specific frames of the generated spectrogram to equal the reference audio (Inpainting).
- **Input:** Boolean Tensor
- **Output:** Masked conditioning tensor
- **Related Feature Groups:** Timbre, Rhythm
- **Expected Influence:** Pinpoint control over which temporal segments are regenerated vs preserved.
- **Risk Level:** LOW
- **Dependency:** `cond_mask`

---

## 3. DIFFUSION TRANSFORMER (DiT) LEVERS

### Lever ID: DIT-001 (Rotary Position Embedding)
- **File:** `src/f5_tts/model/backbones/dit.py`
- **Class:** `DiT`
- **Variable:** `rope`
- **Purpose:** Encodes relative positional information for audio/text sequences.
- **Input:** Sequence length
- **Output:** Sinusoidal embeddings
- **Related Feature Groups:** Rhythm
- **Expected Influence:** Extremely rigid. Manipulating this breaks sequence alignment.
- **Risk Level:** EXTREME (Do not touch during inference)
- **Dependency:** None

### Lever ID: DIT-002 (Text Conditioning Dropout)
- **File:** `src/f5_tts/model/backbones/dit.py`
- **Function:** `get_input_embed`
- **Variable:** `drop_text`, `drop_audio_cond`
- **Purpose:** Used internally for CFG null-prediction branch.
- **Input:** Boolean
- **Output:** Zeroed-out conditioning embeddings
- **Related Feature Groups:** All
- **Expected Influence:** Zeroing out audio_cond forces the model to synthesize a generic voice instead of cloning the reference.
- **Risk Level:** HIGH
- **Dependency:** `cfg_strength`
