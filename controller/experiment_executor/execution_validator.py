"""
execution_validator.py
Validates the execution artifacts after an inference run.
Return PASS or FAIL only. No audio analysis.
"""

import os
import json
from executor_schema import EXPECTED_ARTIFACTS

def validate_execution(execution_dir, execution_id=None, registry=None):
    """
    Checks that all expected artifacts are present in the execution directory.
    Additionally checks traceability and registry records.
    
    Args:
        execution_dir: Path to the execution artifacts folder.
        execution_id: UUID of the execution (optional for backward compatibility).
        registry: ExecutionRegistry instance (optional).
        
    Returns:
        bool: True if PASS, False if FAIL.
    """
    if not os.path.exists(execution_dir):
        print(f"[ExecutionValidator] FAIL: Directory missing {execution_dir}")
        return False
        
    for artifact in EXPECTED_ARTIFACTS:
        path = os.path.join(execution_dir, artifact)
        if not os.path.exists(path):
            print(f"[ExecutionValidator] FAIL: Missing artifact '{artifact}' in {execution_dir}")
            return False
            
    # ── Verify Traceability in Manifest ──
    manifest_path = os.path.join(execution_dir, "execution_manifest.json")
    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
        if "traceability" not in manifest:
            print(f"[ExecutionValidator] FAIL: Missing 'traceability' in {manifest_path}")
            return False
            
        trace = manifest["traceability"]
        required_trace = ["execution_id", "experiment_id", "planner_version", 
                          "reasoning_version", "knowledge_graph_version", 
                          "dataset_version", "benchmark_version", "executor_version"]
        for t in required_trace:
            if t not in trace:
                print(f"[ExecutionValidator] FAIL: Missing '{t}' in traceability of {manifest_path}")
                return False
    except Exception as e:
        print(f"[ExecutionValidator] FAIL: Could not read manifest: {e}")
        return False
        
    # ── Verify Registry Record ──
    if registry and execution_id:
        record = registry.get_record(execution_id)
        if not record:
            print(f"[ExecutionValidator] FAIL: Execution {execution_id} missing from registry.")
            return False
            
    print(f"[ExecutionValidator] PASS: All artifacts and traceability found in {execution_dir}")
    return True

def validate_entire_registry(registry):
    """
    Verifies every registry record points to an existing execution folder.
    Returns PASS / FAIL.
    """
    records = registry.get_all_records()
    for r in records:
        exec_dir = r.get("execution_directory")
        if not exec_dir or not os.path.exists(exec_dir):
            print(f"[ExecutionValidator] FAIL: Registry record {r.get('execution_id')} points to missing folder {exec_dir}")
            return False
    return True
