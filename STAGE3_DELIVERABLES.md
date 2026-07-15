# F5-TTS — STAGE 3 DELIVERABLES
# Decision Engine Architecture

---

## 1. Updated Directory Tree

```text
F5_Hack_Workspace/
├── benchmark/                          (Stage 1)
│   ├── analyzers/
│   ├── visualization/
│   ├── reports/
│   ├── benchmark_config.py
│   ├── feature_registry.py
│   ├── feature_vector.py
│   ├── difference_engine.py
│   ├── controller_interface.py
│   ├── benchmark.py
│   └── validate_benchmark.py
│
├── controller/                         (Stage 1.5)
│   ├── feature_database.py
│   ├── experiment_database.py
│   ├── parameter_registry.py
│   ├── parameter_space.py
│   ├── decision_interface.py
│   ├── controller_output.py
│   │
│   └── decision_engine/                (Stage 3 — NEW)
│       ├── controller_schema.py
│       ├── confidence_estimator.py
│       ├── parameter_recommender.py
│       ├── rule_engine.py
│       └── decision_engine.py
│
├── Knowledge Base/                     (Stage 2)
│   ├── lever_profiles.md
│   ├── feature_lever_matrix.md
│   ├── parameter_accessibility.md
│   ├── priority_score.md
│   ├── parameter_map.md
│   ├── parameter_graph.md
│   └── intervention_priority.md
│
└── PROJECT_OVERVIEW.md
```

---

## 2. Module Responsibilities

| Module | Responsibility |
| :--- | :--- |
| `controller_schema.py` | Exports the stable JSON schema contract for `controller_output.json`. Schema must not change without versioning. |
| `confidence_estimator.py` | Receives triggered rules + feature vector. Returns a per-lever confidence score in `[0, 1]`. No AI — voting heuristic. |
| `parameter_recommender.py` | Exposes the interface for mapping rule outputs to concrete parameter deltas. |
| `rule_engine.py` | Evaluates the `difference` dict from `report.json` against a hardcoded threshold table. Returns triggered rules, reasoning strings, and warnings. |
| `decision_engine.py` | **Main Orchestrator.** Loads inputs, executes pipeline (rules → parameters → confidence), exports `controller_output.json`. |

---

## 3. Pipeline Diagram

```
controller_input.json
        │
        ▼
[decision_engine.py]
        │
        ├──> Load difference dict
        │
        ├──> rule_engine.evaluate_rules()
        │         │
        │         ├── Triggered rules
        │         ├── Reasoning strings
        │         └── Warnings
        │
        ├──> _apply_rules_to_parameters()     ← Rule-based delta table, clamped to bounds
        │
        ├──> _estimate_confidence_from_rules() ← Rule vote counting, normalised [0,1]
        │
        └──> Export controller_output.json
```

---

## 4. JSON Schemas

### Input (`controller_input.json`)
```json
{
    "feature_vector_version": 1,
    "feature_vector_path": "feature_vector.npy",
    "difference": {
        "rhythm_speech_rate_difference": 8.5,
        "energy_rms_mean_difference": -0.07,
        "pitch_f0_mean_difference": -2.1,
        "vq_harmonic_ratio_difference": -0.05
    },
    "metadata": {
        "analysis_version": "1.1.0",
        "feature_vector_version": 1,
        "timestamp": "20260714_171800"
    }
}
```

### Output (`controller_output.json`)
```json
{
    "experiment_id": "20260714_171800",
    "timestamp": "20260714_172130",
    "recommended_parameters": {
        "speed": 1.1,
        "target_rms": 0.11,
        "cfg_strength": 2.0
    },
    "confidence": {
        "speed": 1.0,
        "target_rms": 1.0
    },
    "reasoning": [
        "[RULE-RHYTHM-001] Triggered (value=8.5000, threshold=5.0): Generated speech rate is significantly faster than reference. Increase speed lever.",
        "[RULE-ENERGY-002] Triggered (value=-0.0700, threshold=-0.05): Generated RMS energy is significantly below reference. Increase target_rms."
    ],
    "warnings": []
}
```

---

## 5. Known Limitations

> **LIMITATION-001:** Rule thresholds are hardcoded in `rule_engine.py::RULES`.
> These are starting guesses, not empirically calibrated values.
> Future stages must calibrate thresholds using real benchmark data.

> **LIMITATION-002:** Parameter deltas in `_RULE_DELTA_MAP` are constant per rule.
> There is no proportionality to the size of the deviation.
> Example: `rhythm_speech_rate_difference = 6.0` and `= 50.0` both trigger `RULE-RHYTHM-001` with the same `+0.1` delta.

> **LIMITATION-003:** The Confidence Estimator uses vote counting, not a statistical model.
> Until real experiment data is accumulated in `ExperimentDatabase`, confidence numbers are not statistically meaningful.

> **LIMITATION-004:** The engine currently handles only 3 levers (speed, target_rms, cfg_strength).
> Levers classified as Tier 2 / Tier 3 in `intervention_priority.md` (e.g., `sway_sampling_coef`, `edit_mask`) are not yet wired.
