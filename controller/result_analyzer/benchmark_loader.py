"""
benchmark_loader.py
Loads benchmark_registry.json and selects benchmarks ready for analysis.
Selects only VALIDATED (or COMPLETED) benchmarks.
Never modifies registry records.
"""

import json
import os

def load_pending_benchmarks(benchmark_registry_path, analysis_registry_path):
    """
    Loads benchmark registry and returns a list of benchmark records
    that need analysis.
    
    Args:
        benchmark_registry_path: Path to benchmark_registry.json
        analysis_registry_path: Path to analysis_registry.json
        
    Returns:
        list: Benchmark records ready for analysis.
    """
    if not os.path.exists(benchmark_registry_path):
        print(f"[BenchmarkLoader] WARNING: Benchmark registry not found at {benchmark_registry_path}")
        return []
        
    with open(benchmark_registry_path, "r", encoding="utf-8") as f:
        bench_registry = json.load(f)
        
    # Load analysis registry to filter out already analyzed ones
    analyzed_benchmark_ids = set()
    if os.path.exists(analysis_registry_path):
        with open(analysis_registry_path, "r", encoding="utf-8") as f:
            analysis_registry = json.load(f)
            for r in analysis_registry.get("records", []):
                analyzed_benchmark_ids.add(r["benchmark_id"])
                
    runnable = []
    for record in bench_registry.get("records", []):
        status = record.get("benchmark_status")
        # Accept COMPLETED or VALIDATED since Stage 9 writes COMPLETED to registry prior to validation
        if status in ["VALIDATED", "COMPLETED"]:
            if record["benchmark_id"] not in analyzed_benchmark_ids:
                runnable.append(record)
                
    print(f"[BenchmarkLoader] Found {len(runnable)} benchmarks ready for analysis.")
    return runnable
