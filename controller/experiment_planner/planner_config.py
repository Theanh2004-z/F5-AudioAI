"""
planner_config.py
Planner constants and configurable thresholds.

No hard-coded parameter values (no speed=1.0, no cfg_strength=2.0, etc.).
All tunable settings are about the planner's own behaviour, not about F5.
"""

# ── Hypothesis filtering ────────────────────────────────────────────────────

# Lever hypotheses with reasoning_confidence below this are skipped.
# This prevents planning useless experiments on untrustworthy observations.
MIN_CONFIDENCE_THRESHOLD = 0.15

# Lever hypotheses with conflict_count above this are flagged but still planned.
# High conflict does NOT block an experiment — it adds a warning.
MAX_ACCEPTABLE_CONFLICT_COUNT = 2

# ── Sweep generation ────────────────────────────────────────────────────────

# Default number of steps per PARAMETER_SWEEP experiment.
DEFAULT_STEP_COUNT = 5

# Default number of steps per BOUNDARY_PROBE experiment.
BOUNDARY_PROBE_STEP_COUNT = 2

# The planner generates at most this many experiments per lever hypothesis.
MAX_EXPERIMENTS_PER_LEVER = 2

# ── Safety gate ─────────────────────────────────────────────────────────────

# Levers marked with these safety classes are excluded from planning.
# EXTREME_RISK levers must NEVER appear in any experiment plan.
BLOCKED_SAFETY_CLASSES = {"EXTREME_RISK"}

# ── Scheduling ───────────────────────────────────────────────────────────────

# Default scheduling strategy.
# See planner_schema.SCHEDULING_STRATEGIES for options.
DEFAULT_SCHEDULING_STRATEGY = "SAFETY_FIRST"

# Priority scores assigned to each safety class (lower = scheduled first).
SAFETY_PRIORITY_MAP = {
    "HIGH":         1,
    "MEDIUM":       2,
    "LOW":          3,
    "EXTREME_RISK": 999  # Should never appear due to BLOCKED_SAFETY_CLASSES
}

# ── Validation ───────────────────────────────────────────────────────────────

# Maximum number of values allowed in a parameter_range list.
MAX_RANGE_VALUES = 10

# Minimum number of values required in a parameter_range list.
MIN_RANGE_VALUES = 2
