"""
analysis_validator.py
Validates the analysis artifacts after a run.
Return PASS or FAIL only.
"""

import os
import json
from analyzer_schema import EXPECTED_ARTIFACTS

def validate_analysis(analysis_dir, analysis_id, registry):
    """
    Checks that all expected artifacts are present in the analysis directory
    and that the registry has been updated.
    
    Args:
        analysis_dir: Path to the analysis artifacts folder.
        analysis_id: ID of the analysis run.
        registry: AnalysisRegistry instance.
        
    Returns:
        bool: True if PASS, False if FAIL.
    """
    if not os.path.exists(analysis_dir):
        print(f"[AnalysisValidator] FAIL: Directory missing {analysis_dir}")
        return False
        
    for artifact in EXPECTED_ARTIFACTS:
        path = os.path.join(analysis_dir, artifact)
        if not os.path.exists(path):
            print(f"[AnalysisValidator] FAIL: Missing artifact '{artifact}' in {analysis_dir}")
            return False
            
    # Check registry
    found = False
    for r in registry._registry["records"]:
        if r["analysis_id"] == analysis_id:
            found = True
            break
            
    if not found:
        print(f"[AnalysisValidator] FAIL: Analysis {analysis_id} not found in registry.")
        return False
        
    # Check traceability inside manifest
    manifest_path = os.path.join(analysis_dir, "analysis_manifest.json")
    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
        trace = manifest.get("traceability", {})
        required_trace = ["benchmark_id", "execution_id", "experiment_id", 
                          "planner_version", "reasoning_version", "executor_version", 
                          "benchmark_version", "analysis_version"]
        for t in required_trace:
            if t not in trace:
                print(f"[AnalysisValidator] FAIL: Missing '{t}' in traceability of {manifest_path}")
                return False
    except Exception as e:
        print(f"[AnalysisValidator] FAIL: Could not read manifest: {e}")
        return False
            
    print(f"[AnalysisValidator] PASS: All artifacts and registry record found for {analysis_dir}")
    return True
