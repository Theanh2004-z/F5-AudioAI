"""
benchmark_worker.py
Main Orchestrator for Stage 9 — Benchmark Worker.
Processes completed executions through the benchmark pipeline deterministically.
"""

import os
import sys
import json
import time
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from worker_schema          import WORKER_VERSION
from execution_loader       import load_pending_executions
from benchmark_runner       import run_benchmark
from benchmark_registry     import BenchmarkRegistry
from benchmark_logger       import BenchmarkLogger
from benchmark_validator    import validate_benchmark

REPORT_FILENAME = "benchmark_worker_report.json"

def write_json_artifact(target_dir, filename, data):
    """Writes a JSON artifact to the execution directory."""
    path = os.path.join(target_dir, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def get_traceability(exec_manifest_path, bench_id, exec_id, bench_version):
    """Extracts traceability from execution manifest and augments it."""
    trace = {}
    if os.path.exists(exec_manifest_path):
        with open(exec_manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
            trace = manifest.get("traceability", {})
            
    return {
        "benchmark_id":            bench_id,
        "execution_id":            exec_id,
        "experiment_id":           trace.get("experiment_id", "UNKNOWN"),
        "planner_version":         trace.get("planner_version", "UNKNOWN"),
        "reasoning_version":       trace.get("reasoning_version", "UNKNOWN"),
        "knowledge_graph_version": trace.get("knowledge_graph_version", "UNKNOWN"),
        "dataset_version":         trace.get("dataset_version", "UNKNOWN"),
        "executor_version":        trace.get("executor_version", "UNKNOWN"),
        "benchmark_version":       bench_version
    }

def run_benchmark_worker(exec_registry_path, output_dir="benchmarks", reference_audio="reference.wav"):
    """
    Runs the Benchmark Worker pipeline.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs(output_dir, exist_ok=True)
    
    registry = BenchmarkRegistry(registry_dir=output_dir)
    
    # ── 1. Load Executions ──────────────────────────────────────────────────
    pending_executions = load_pending_executions(
        exec_registry_path, registry.registry_path
    )
    
    summary = {
        "total_executions_loaded": len(pending_executions),
        "total_benchmarks_attempted": 0,
        "total_completed": 0,
        "total_failed": 0,
        "total_validated": 0
    }
    
    benchmark_records = []
    
    # ── 2. Processing Loop ─────────────────────────────────────────────────
    for exec_record in pending_executions:
        exec_id = exec_record["execution_id"]
        exec_dir = exec_record["execution_directory"]
        generated_audio = os.path.join(exec_dir, "generated.wav")
        exec_manifest = os.path.join(exec_dir, exec_record.get("artifact_manifest", "execution_manifest.json"))
        
        summary["total_benchmarks_attempted"] += 1
        
        logger = BenchmarkLogger(exec_id, benchmark_version="1.0.0")
        bench_dir = os.path.join(output_dir, logger.benchmark_id)
        os.makedirs(bench_dir, exist_ok=True)
        
        print(f"\n[Worker] Starting benchmark for execution {exec_id} → {bench_dir}")
        
        try:
            # ── Run Benchmark ─────────────────────────────────────────────
            logger.start()
            
            if not os.path.exists(generated_audio):
                # We skip missing files gracefully.
                raise FileNotFoundError(f"Generated audio not found: {generated_audio}")
                
            success = run_benchmark(reference_audio, generated_audio, bench_dir)
            
            if not success:
                raise RuntimeError("Benchmark runner returned False.")
                
            logger.stop(success=True)
            summary["total_completed"] += 1
            
        except Exception as e:
            logger.stop(success=False, error=e)
            summary["total_failed"] += 1
            print(f"[Worker] ERROR during benchmark: {e}")
            
        # ── Save Artifacts (Runtime & Manifest) ───────────────────────────
        runtime_record = logger.get_runtime_record()
        write_json_artifact(bench_dir, "benchmark_runtime.json", runtime_record)
        
        traceability = get_traceability(
            exec_manifest, logger.benchmark_id, exec_id, logger.benchmark_version
        )
        
        manifest = {
            "benchmark_id": logger.benchmark_id,
            "execution_id": exec_id,
            "experiment_id": traceability["experiment_id"],
            "timestamp": logger.start_time if logger.start_time else time.time(),
            "worker_version": WORKER_VERSION,
            "traceability": traceability
        }
        write_json_artifact(bench_dir, "benchmark_manifest.json", manifest)
        
        # ── Update Benchmark Registry ─────────────────────────────────────
        reg_record = {
            "benchmark_id": logger.benchmark_id,
            "execution_id": exec_id,
            "experiment_id": traceability["experiment_id"],
            "benchmark_timestamp": logger.start_time if logger.start_time else time.time(),
            "benchmark_directory": bench_dir,
            "benchmark_status": logger.status,
            "benchmark_version": logger.benchmark_version
        }
        registry.register(reg_record)
        
        # ── Validate ──────────────────────────────────────────────────────
        is_valid = validate_benchmark(bench_dir, logger.benchmark_id, registry)
        if is_valid:
            summary["total_validated"] += 1
            final_status = "VALIDATED"
        else:
            final_status = "INVALID" if logger.status == "COMPLETED" else "FAILED"
            
        benchmark_records.append({
            "benchmark_id": logger.benchmark_id,
            "execution_id": exec_id,
            "status": final_status,
            "benchmark_dir": bench_dir,
            "duration_sec": runtime_record["duration_sec"],
            "error_message": logger.error_message
        })
        
    # ── Export Report ─────────────────────────────────────────────────────
    report = {
        "metadata": {
            "worker_version": WORKER_VERSION,
            "timestamp": timestamp,
            "execution_registry_file": os.path.basename(exec_registry_path)
        },
        "summary": summary,
        "benchmark_records": benchmark_records
    }
    
    report_path = os.path.join(output_dir, REPORT_FILENAME)
    write_json_artifact(output_dir, REPORT_FILENAME, report)
    
    print(f"\n[Worker] Pipeline finished. Report saved to {report_path}")
    return report

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="F5-TTS Benchmark Worker")
    parser.add_argument("--exec_registry", required=True, help="Path to execution_registry.json")
    parser.add_argument("--output_dir", default="benchmarks", help="Output directory")
    parser.add_argument("--reference", default="reference.wav", help="Path to reference audio")
    args = parser.parse_args()
    
    run_benchmark_worker(args.exec_registry, args.output_dir, args.reference)
