# F5-TTS INFERENCE PIPELINE: INTERVENTION PRIORITY
*(Reverse Engineering Document - No Optimization)*

This document ranks the discovered intervention points (Levers) based on their suitability for the external AI Controller. 

**Criteria:**
- **Isolation:** Does it change only one specific acoustic feature without side-effects?
- **Safety:** Will extreme values break the model (artifacts/noise) or just degrade gracefully?
- **Controllability:** Is the relationship linear/predictable?

---

## 🟢 TIER 1: PRIME CANDIDATES (Safest & Most Isolated)
These levers should be exposed to the AI Controller immediately.

### 1. `speed` (PRE-001)
- **Isolation:** HIGH. Only stretches/squashes time.
- **Safety:** HIGH. Safe within [0.5, 2.0] range.
- **Controllability:** EXCELLENT. Linear correlation to Rhythm (Speech Rate).

### 2. `target_rms` (PRE-002)
- **Isolation:** HIGH. Only scales amplitude.
- **Safety:** HIGH. Clipping handled gracefully by post-processing.
- **Controllability:** EXCELLENT. Direct multiplier to Energy (RMS Mean/Peak).

### 3. `cross_fade_duration` (PRE-003)
- **Isolation:** MEDIUM. Affects pause duration and transition smoothness.
- **Safety:** HIGH. Very predictable behavior.
- **Controllability:** GOOD.

---

## 🟡 TIER 2: EXPLORATORY CANDIDATES (Powerful but Entangled)
These levers change multiple features simultaneously.

### 4. `cfg_strength` (CFM-002)
- **Isolation:** LOW. Simultaneously forces Pitch, Energy, and Timbre adherence.
- **Safety:** MEDIUM. Values > 3.0 cause robotic voice or severe distortion.
- **Controllability:** MODERATE. Non-linear threshold behavior.

### 5. `edit_mask` (CFM-004)
- **Isolation:** HIGH. Pinpoint spatial isolation.
- **Safety:** HIGH. Forces model to regurgitate original audio.
- **Controllability:** EXCELLENT, but requires external VAD/ASR logic to generate the mask.

---

## 🔴 TIER 3: DANGEROUS CANDIDATES (Do Not Expose to AI Controller)
Modifying these dynamically per-generation is highly discouraged.

### 6. `sway_sampling_coef` (CFM-003)
- **Isolation:** LOW. Warps entire frequency spectrum integration.
- **Safety:** LOW. Can result in complete failure to generate speech.
- **Controllability:** POOR. Highly unpredictable non-linear effects on Voice Quality.

### 7. `nfe_step` (CFM-001)
- **Isolation:** POOR.
- **Safety:** HIGH. (Higher is always better, just slower).
- **Controllability:** NONE. Not a stylistic parameter, strictly a quality/compute trade-off.

### 8. `drop_audio_cond` / `drop_text` (DIT-002)
- **Isolation:** N/A.
- **Safety:** LOW. Destroys the conditioning path.
- **Controllability:** NONE. Used strictly for CFG mathematical routing.
