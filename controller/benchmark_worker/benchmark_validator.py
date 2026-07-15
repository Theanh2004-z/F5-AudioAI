"""
benchmark_validator.py
Validates the benchmark artifacts after a run.
Return PASS or FAIL only. No quality evaluation.
"""

import os
from worker_schema import EXPECTED_ARTIFACTS

def validate_benchmark(benchmark_dir, benchmark_id, registry):
    """
    Checks that all expected artifacts are present in the benchmark directory
    and that the registry has been updated.
    
    Args:
        benchmark_dir: Path to the benchmark artifacts folder.
        benchmark_id: ID of the benchmark run.
        registry: BenchmarkRegistry instance.
        
    Returns:
        bool: True if PASS, False if FAIL.
    """
    if not os.path.exists(benchmark_dir):
        print(f"[BenchmarkValidator] FAIL: Directory missing {benchmark_dir}")
        return False
        
    for artifact in EXPECTED_ARTIFACTS:
        path = os.path.join(benchmark_dir, artifact)
        if not os.path.exists(path):
            print(f"[BenchmarkValidator] FAIL: Missing artifact '{artifact}' in {benchmark_dir}")
            return False
            
    # Check registry
    found = False
    for r in registry._registry["records"]:
        if r["benchmark_id"] == benchmark_id:
            found = True
            break
            
    if not found:
        print(f"[BenchmarkValidator] FAIL: Benchmark {benchmark_id} not found in registry.")
        return False
            
    print(f"[BenchmarkValidator] PASS: All artifacts and registry record found for {benchmark_dir}")
    return True
