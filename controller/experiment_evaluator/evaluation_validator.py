"""
evaluation_validator.py
Validates the evaluation artifacts after a run.
Return PASS or FAIL only.
"""

import os
import json
from evaluator_schema import EXPECTED_ARTIFACTS

def validate_evaluation(evaluation_dir, evaluation_id, registry):
    """
    Checks that all expected artifacts are present in the evaluation directory
    and that the registry has been updated.
    
    Args:
        evaluation_dir: Path to the evaluation artifacts folder.
        evaluation_id: ID of the evaluation run.
        registry: EvaluationRegistry instance.
        
    Returns:
        bool: True if PASS, False if FAIL.
    """
    if not os.path.exists(evaluation_dir):
        print(f"[EvaluationValidator] FAIL: Directory missing {evaluation_dir}")
        return False
        
    for artifact in EXPECTED_ARTIFACTS:
        path = os.path.join(evaluation_dir, artifact)
        if not os.path.exists(path):
            print(f"[EvaluationValidator] FAIL: Missing artifact '{artifact}' in {evaluation_dir}")
            return False
            
    # Check registry
    found = False
    for r in registry._registry["records"]:
        if r["evaluation_id"] == evaluation_id:
            found = True
            break
            
    if not found:
        print(f"[EvaluationValidator] FAIL: Evaluation {evaluation_id} not found in registry.")
        return False
        
    # Check traceability inside manifest
    manifest_path = os.path.join(evaluation_dir, "evaluation_manifest.json")
    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
        trace = manifest.get("traceability", {})
        required_trace = ["analysis_id", "benchmark_id", "execution_id", "experiment_id",
                          "planner_version", "reasoning_version", "executor_version",
                          "benchmark_version", "analysis_version", "evaluation_version",
                          "evaluation_profile_version", "feature_registry_version",
                          "decision_explainer_version",
                          "baseline_id", "baseline_version",
                          "rule_engine_version", "rule_registry_version"]
        for t in required_trace:
            if t not in trace:
                print(f"[EvaluationValidator] FAIL: Missing '{t}' in traceability of {manifest_path}")
                return False
    except Exception as e:
        print(f"[EvaluationValidator] FAIL: Could not read manifest: {e}")
        return False
            
    print(f"[EvaluationValidator] PASS: All artifacts and registry record found for {evaluation_dir}")
    return True
