"""
plan_loader.py
Loads experiment_plan.json and validates its schema.
Never modifies the plan. Returns the list of planned experiments.
"""

import json
import os


def load_plan(plan_path):
    """
    Loads and validates the experiment plan.
    
    Args:
        plan_path: Path to experiment_plan.json
        
    Returns:
        dict: The full plan.
        list: The planned_experiments extracted from the plan.
    """
    if not os.path.exists(plan_path):
        raise FileNotFoundError(f"[PlanLoader] Plan file not found: {plan_path}")
        
    with open(plan_path, "r", encoding="utf-8") as f:
        plan = json.load(f)
        
    if "planned_experiments" not in plan:
        raise ValueError("[PlanLoader] Invalid schema: Missing 'planned_experiments' key.")
        
    experiments = plan["planned_experiments"]
    
    # Filter out DUPLICATEs or CANCELLED if they exist, executor only runs PLANNED
    runnable = []
    for exp in experiments:
        status = exp.get("execution_status", "UNKNOWN")
        if status == "PLANNED":
            runnable.append(exp)
            
    print(f"[PlanLoader] Loaded {len(experiments)} experiments. {len(runnable)} are runnable (PLANNED).")
    
    return plan, runnable
