# Stage 7 Revision 2: Production-Grade Experiment Planning System

## 1. Updated Directory Tree

```text
controller/experiment_planner/
├── planner_schema.py        ← Defines JSON schema (v1.2.0), statuses, tags, and strategies
├── planner_config.py        ← Configures boundaries, sweeps, and acceptable safety
├── hypothesis_ranker.py     ← Filters and ranks incoming hypotheses by confidence
├── experiment_generator.py  ← Constructs full Manifests (Fingerprint, UUID, Priority, Cost, Tags, Retry)
├── plan_validator.py        ← Enforces 11 validation gates and handles Duplicate Detection
├── experiment_scheduler.py  ← Sequences valid experiments using scheduling strategy
└── experiment_planner.py    ← Orchestrator, assembling final planner_statistics and report
```

## 2. Module Responsibilities

- **`planner_schema.py`**: Declares valid statuses (`PLANNED`, `DUPLICATE`, etc.), schema version (`1.2.0`), and documentation for all manifest fields.
- **`planner_config.py`**: Houses configurable rules for planning without hardcoding F5-TTS parameter values.
- **`hypothesis_ranker.py`**: Ensures only robust hypotheses (high reasoning confidence, safe risk level) make it to planning.
- **`experiment_generator.py`**: Generates exhaustive immutable experiment manifests. Embeds UUIDs, computes deterministic `experiment_fingerprint` via SHA256, assigns `experiment_family`, estimates execution cost, computes execution priority, and attaches metadata like `retry_policy`, `experiment_tags`, and `expected_artifacts`.
- **`plan_validator.py`**: Checks uniqueness, ranges, dependencies, and required metadata. Additionally detects duplicate fingerprints. Instead of dropping duplicates, marks them as `DUPLICATE` and links them via `duplicate_of`.
- **`experiment_scheduler.py`**: Evaluates `execution_priority` and scheduling strategy to order experiments for downstream execution.
- **`experiment_planner.py`**: Main driver. Compiles all valid and duplicate experiments into `experiment_plan.json`. Produces robust `planner_statistics` including breakdowns for family, risk, cost, and average dependencies.

## 3. Pipeline

```
Reasoning Report + Registries
           │
           ▼
   hypothesis_ranker         → Filter by confidence and safety
           │
   experiment_generator      → Build Manifests (UUID, Fingerprint, Cost, Priority, Tags)
           │
     plan_validator          → 11-step validation + Duplicate Detection
           │
   experiment_scheduler      → Sequence by strategy & computed priority
           │
           ▼
  experiment_plan.json       (with expanded planner_statistics)
```

## 4. Example Experiment Manifest (Schema)

```json
{
    "experiment_id": "EXP-a8c93b2f",
    "experiment_fingerprint": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "experiment_family": "CFG_STRENGTH_EXPLORATION",
    "parent_reasoning_report": "reasoning_report.json",
    "hypothesis_id": "HYP-cfg_strength",
    "target_lever": "cfg_strength",
    "experiment_type": "PARAMETER_SWEEP",
    "objective": "Sweep cfg_strength uniformly across its full range...",
    "creation_timestamp": "20260714_233000",
    "planner_version": "1.2.0",
    "execution_status": "PLANNED",
    "provenance": {
        "generated_by": "experiment_planner",
        "reasoning_engine_version": "1.0.0",
        "knowledge_graph_version": "1.0.0",
        "dataset_version": "1.0.0"
    },
    "reproducibility": { ... },
    "expected_observations": ["pitch_f0_mean"],
    "success_criteria": [
        {
            "feature": "pitch_f0_mean",
            "expected_direction": "unknown"
        }
    ],
    "rollback_metadata": {
        "enabled": true,
        "restore_previous_parameters": true
    },
    "dependencies": [],
    "risk_level": "MEDIUM",
    "cost_estimation": {
        "estimated_runtime": "MEDIUM",
        "estimated_gpu_memory": "MEDIUM",
        "estimated_disk_usage": "MEDIUM",
        "estimated_outputs": "MEDIUM"
    },
    "execution_priority": 25,
    "experiment_tags": ["cfg_strength", "parameter_sweep", "medium", "tier1"],
    "retry_policy": {
        "max_retry": 2,
        "retry_on_failure": true,
        "retry_on_timeout": true
    },
    "expected_artifacts": [
        "generated_audio.wav",
        "benchmark_report.json",
        "feature_vector.npy",
        "reasoning_report.json"
    ],
    "parameter_name": "cfg_strength",
    "parameter_range": [1.0, 1.75, 2.5, 3.25, 4.0],
    "step_count": 5,
    "reasoning_confidence": 0.85,
    "safety_class": "MEDIUM",
    "schedule_priority": 50,
    "run_order": 1
}
```

## 5. Planner Metadata (Statistics)

```json
"planner_statistics": {
    "family_breakdown": {
        "CFG_STRENGTH_EXPLORATION": 2,
        "SPEED_EXPLORATION": 1
    },
    "risk_breakdown": {
        "LOW": 1,
        "MEDIUM": 2,
        "HIGH": 0,
        "EXTREME_RISK": 0
    },
    "cost_breakdown": {
        "LOW": 1,
        "MEDIUM": 2,
        "HIGH": 0,
        "EXTREME": 0
    },
    "duplicate_count": 0,
    "average_dependency_count": 0.0
}
```

## 6. Known Limitations

1. **EP-R2-LIM-001**: `execution_priority` is computed purely deterministically based on risk level, runtime estimate, and dependency count. It does not factor in dynamic cluster load or actual available GPU memory since the planner is strictly offline.
2. **EP-R2-LIM-002**: `experiment_fingerprint` uses JSON serialization. If key ordering or spacing changes subtly in the implementation of `_generate_fingerprint()`, the hash will change. We enforce `sort_keys=True` and `separators=(',', ':')` to mitigate this.
3. **EP-R2-LIM-003**: The duplicated experiments are marked as `DUPLICATE` but remain in the output plan. A downstream executor needs to ensure it respects the `execution_status` and skips them, optionally linking the results to `duplicate_of`.
4. **EP-R2-LIM-004**: `cost_estimation` is purely step-count based (qualitative). Real runtime could differ massively depending on target audio length, which the planner does not know.
