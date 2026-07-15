"""
execution_loader.py
Loads execution_registry.json and selects executions ready for benchmarking.
Skips already benchmarked executions.
Never modifies execution records.
"""

import json
import os

def load_pending_executions(execution_registry_path, benchmark_registry_path):
    """
    Loads execution registry and returns a list of execution records
    that need benchmarking.
    
    Args:
        execution_registry_path: Path to execution_registry.json
        benchmark_registry_path: Path to benchmark_registry.json
        
    Returns:
        list: Execution records ready for benchmarking.
    """
    if not os.path.exists(execution_registry_path):
        print(f"[ExecutionLoader] WARNING: Execution registry not found at {execution_registry_path}")
        return []
        
    with open(execution_registry_path, "r", encoding="utf-8") as f:
        exec_registry = json.load(f)
        
    # Load benchmark registry to filter out already benchmarked ones
    benchmarked_execution_ids = set()
    if os.path.exists(benchmark_registry_path):
        with open(benchmark_registry_path, "r", encoding="utf-8") as f:
            bench_registry = json.load(f)
            for r in bench_registry.get("records", []):
                benchmarked_execution_ids.add(r["execution_id"])
                
    runnable = []
    # Note: Stage 8 might register as COMPLETED and then validate. 
    # For robust compatibility, we allow both VALIDATED and COMPLETED if artifacts exist.
    # But per prompt strictness: execution_status == VALIDATED (or COMPLETED if that's what Stage 8 wrote)
    for record in exec_registry.get("records", []):
        status = record.get("execution_status")
        if status in ["VALIDATED", "COMPLETED"]:
            if record["execution_id"] not in benchmarked_execution_ids:
                runnable.append(record)
                
    print(f"[ExecutionLoader] Found {len(runnable)} executions ready for benchmarking.")
    return runnable
