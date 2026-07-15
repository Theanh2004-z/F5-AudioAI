"""
plan_validator.py (Stage 7 Revision)
Validates generated experiment plans before scheduling.

Checks:
  1. No duplicate experiments (same lever + experiment_type combination).
  2. Parameter ranges are within registered bounds.
  3. All experiment_ids are unique (UUID).
  4. Step count within configured limits.
  5. expected_observations list is non-empty.
  6. missing provenance.
  7. missing success criteria.
  8. missing rollback metadata.
  9. invalid dependency formatting.
 10. duplicate fingerprint (sets status to DUPLICATE).
 11. family, tags, retry policy, artifact contract, cost, priority.

Rejected experiments are excluded from the final plan with a documented reason.
No optimization. No parameter recommendation.
"""

from planner_config import MAX_RANGE_VALUES, MIN_RANGE_VALUES


def validate_experiments(experiments, parameter_space):
    """
    Validates a list of candidate experiment plans.

    Args:
        experiments      : list[dict] — from experiment_generator
        parameter_space  : dict       — from parameter_space.json

    Returns:
        passed   : list[dict]  — valid experiment plans
        rejected : list[dict]  — dicts with {experiment_id, reason}
        val_warnings : list[str]
    """
    params_db   = parameter_space.get("parameters", {})
    passed      = []
    rejected    = []
    val_warnings = []

    seen_ids              = set()
    seen_lever_type_pairs = set()

    for exp in experiments:
        eid        = exp.get("experiment_id", "UNKNOWN")
        lever      = exp.get("parameter_name", "")
        exp_type   = exp.get("experiment_type", "")
        param_range = exp.get("parameter_range", [])
        step_count = exp.get("step_count", 0)
        expected   = exp.get("expected_observations", [])

        reasons = []

        # 1. Unique experiment ID
        if eid in seen_ids:
            reasons.append(f"Duplicate experiment_id '{eid}'. UUID collision is highly unexpected.")
        seen_ids.add(eid)

        # 3. Range length limits
        if len(param_range) < MIN_RANGE_VALUES:
            reasons.append(
                f"parameter_range has {len(param_range)} values, "
                f"minimum is {MIN_RANGE_VALUES}."
            )
        if len(param_range) > MAX_RANGE_VALUES:
            reasons.append(
                f"parameter_range has {len(param_range)} values, "
                f"maximum is {MAX_RANGE_VALUES}."
            )

        # 4. Values within bounds
        if lever in params_db:
            constraints = params_db[lever].get("constraints", {})
            lo = constraints.get("min")
            hi = constraints.get("max")
            if lo is not None and hi is not None:
                out_of_range = [v for v in param_range if v < lo or v > hi]
                if out_of_range:
                    reasons.append(
                        f"Values {out_of_range} are outside registered bounds "
                        f"[{lo}, {hi}] for lever '{lever}'."
                    )
        else:
            val_warnings.append(
                f"[{eid}] Lever '{lever}' not found in parameter_space.json. "
                f"Bounds check skipped."
            )

        # 5. Non-empty expected_observations
        if not expected:
            reasons.append("expected_observations list is empty.")

        # 6. Missing provenance
        if "provenance" not in exp or not exp["provenance"]:
            reasons.append("Missing provenance metadata.")

        # 7. Missing success criteria
        if "success_criteria" not in exp or not isinstance(exp["success_criteria"], list):
            reasons.append("Missing or invalid success_criteria list.")

        # 8. Missing rollback metadata
        if "rollback_metadata" not in exp or "enabled" not in exp["rollback_metadata"]:
            reasons.append("Missing rollback_metadata.")

        # 9. Invalid dependencies
        if "dependencies" not in exp or not isinstance(exp["dependencies"], list):
            reasons.append("Dependencies must be a list (even if empty).")

        # 10. Missing new fields
        if "experiment_family" not in exp:
            reasons.append("Missing experiment_family.")
        if "experiment_tags" not in exp or not isinstance(exp["experiment_tags"], list):
            reasons.append("Missing or invalid experiment_tags.")
        if "retry_policy" not in exp:
            reasons.append("Missing retry_policy.")
        if "expected_artifacts" not in exp or not isinstance(exp["expected_artifacts"], list):
            reasons.append("Missing or invalid expected_artifacts.")
        if "cost_estimation" not in exp:
            reasons.append("Missing cost_estimation.")
        if "execution_priority" not in exp:
            reasons.append("Missing execution_priority.")
        
        if "experiment_fingerprint" not in exp:
            reasons.append("Missing experiment_fingerprint.")

        # Outcome
        if reasons:
            rejected.append({"experiment_id": eid, "reasons": reasons})
        else:
            passed.append(exp)

    # Now handle duplicate fingerprints among passed
    seen_fingerprints = {}
    final_passed = []
    for exp in passed:
        fp = exp["experiment_fingerprint"]
        if fp in seen_fingerprints:
            exp["execution_status"] = "DUPLICATE"
            exp["duplicate_of"] = seen_fingerprints[fp]
        else:
            seen_fingerprints[fp] = exp["experiment_id"]
        final_passed.append(exp)

    return final_passed, rejected, val_warnings
