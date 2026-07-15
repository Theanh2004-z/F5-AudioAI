"""
experiment_scheduler.py
Orders validated experiment plans for future execution.

Scheduling strategies:
  SAFETY_FIRST     : Highest safety class experiments run first.
  CONFIDENCE_FIRST : Highest reasoning_confidence experiments run first.
  ISOLATION_FIRST  : Lowest coupling levers run first (not yet implemented,
                     requires coupling metadata from parameter_registry).

This module does NOT execute experiments.
It only assigns schedule_priority integers to each plan entry.
Future stages will consume the priority field for actual sequencing.

No optimization. No parameter tuning. No F5 calls.
"""

from planner_config import DEFAULT_SCHEDULING_STRATEGY, SAFETY_PRIORITY_MAP


def schedule_experiments(validated_experiments, strategy=DEFAULT_SCHEDULING_STRATEGY):
    """
    Assigns a schedule_priority to each validated experiment and returns
    a sorted list ready for the final plan.

    Args:
        validated_experiments : list[dict] — passed experiments from plan_validator
        strategy              : str        — scheduling strategy name

    Returns:
        scheduled    : list[dict]  — experiments with schedule_priority added
        sched_warnings : list[str]
    """
    sched_warnings = []
    scheduled      = []

    for exp in validated_experiments:
        safety = exp.get("safety_class", "UNKNOWN")
        conf   = exp.get("reasoning_confidence", 0.0)

        if strategy == "SAFETY_FIRST":
            priority = SAFETY_PRIORITY_MAP.get(safety, 50)

        elif strategy == "CONFIDENCE_FIRST":
            # Invert confidence so higher confidence = lower (earlier) priority number
            # Map [0,1] → [1, 100] descending
            priority = max(1, int((1.0 - conf) * 100))

        elif strategy == "ISOLATION_FIRST":
            # Placeholder: coupling metadata not yet available at schedule time.
            # Falls back to SAFETY_FIRST.
            priority = SAFETY_PRIORITY_MAP.get(safety, 50)
            sched_warnings.append(
                f"[{exp['experiment_id']}] ISOLATION_FIRST strategy not yet fully "
                f"implemented. Falling back to SAFETY_FIRST priority."
            )
        else:
            sched_warnings.append(
                f"Unknown strategy '{strategy}'. Defaulting to SAFETY_FIRST."
            )
            priority = SAFETY_PRIORITY_MAP.get(safety, 50)

        scheduled.append({**exp, "schedule_priority": priority})

    # Sort by ascending priority (lower = earlier)
    scheduled.sort(key=lambda x: (x["schedule_priority"], -x["reasoning_confidence"]))

    # Reassign sequential run-order after sorting
    for i, exp in enumerate(scheduled):
        exp["run_order"] = i + 1

    return scheduled, sched_warnings
