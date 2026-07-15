"""
experiment_executor.py
Main Orchestrator for Stage 8 — Experiment Executor.
Executes the planned experiments deterministically. No optimization or decision logic.
"""

import os
import sys
import json
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from executor_schema        import EXECUTOR_VERSION
from plan_loader            import load_plan
from parameter_applier      import extract_inference_kwargs
from inference_runner       import run_inference
from artifact_manager       import setup_execution_directory, write_json_artifact, setup_log_files
from execution_logger       import ExecutionLogger
from execution_validator    import validate_execution, validate_entire_registry
from execution_registry     import ExecutionRegistry

REPORT_FILENAME = "execution_report.json"

def run_executor(plan_path, output_dir="executions"):
    """
    Runs the Experiment Executor pipeline on a given plan file.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs(output_dir, exist_ok=True)
    
    # ── 1. Load Plan ───────────────────────────────────────────────────────
    full_plan, runnable_experiments = load_plan(plan_path)
    
    registry = ExecutionRegistry(registry_dir=output_dir)
    initial_registry_count = registry.total_registered
    duplicate_records = 0
    
    summary = {
        "total_experiments_loaded":   len(runnable_experiments),
        "total_executions_attempted": 0,
        "total_completed":            0,
        "total_failed":               0,
        "total_validated":            0
    }
    execution_records = []
    
    # ── 2. Execution Loop ──────────────────────────────────────────────────
    for experiment in runnable_experiments:
        exp_id = experiment["experiment_id"]
        
        # A plan can have a parameter_range. If step_count > 1, we should theoretically run
        # a sweep. For this architecture, we run 1 execution per step in the range.
        step_count = experiment.get("step_count", 1)
        
        for step_idx in range(step_count):
            summary["total_executions_attempted"] += 1
            
            # Setup Artifacts
            exec_dir = setup_execution_directory(exp_id, base_dir=output_dir)
            stdout_path, stderr_path = setup_log_files(exec_dir)
            logger = ExecutionLogger(exp_id)
            
            print(f"\n[Executor] Starting execution for {exp_id} (Step {step_idx+1}/{step_count}) → {exec_dir}")
            
            try:
                # ── Apply Parameters ──────────────────────────────────────
                kwargs = extract_inference_kwargs(experiment, step_index=step_idx)
                
                # Write experiment manifest snapshot with traceability
                # We inject the specific kwargs applied for this step
                manifest_snapshot = dict(experiment)
                manifest_snapshot["applied_parameters"] = kwargs
                
                # Traceability injection
                traceability = {
                    "execution_id": logger.execution_id,
                    "experiment_id": exp_id,
                    "planner_version": experiment.get("planner_version", "UNKNOWN"),
                    "reasoning_version": experiment.get("provenance", {}).get("reasoning_engine_version", "UNKNOWN"),
                    "knowledge_graph_version": experiment.get("provenance", {}).get("knowledge_graph_version", "UNKNOWN"),
                    "dataset_version": experiment.get("provenance", {}).get("dataset_version", "UNKNOWN"),
                    "benchmark_version": "1.0.0", # Hardcoded for now
                    "executor_version": EXECUTOR_VERSION
                }
                manifest_snapshot["traceability"] = traceability
                
                write_json_artifact(exec_dir, "execution_manifest.json", manifest_snapshot)
                
                # ── Run F5 Inference ──────────────────────────────────────
                logger.start()
                success = run_inference(kwargs, exec_dir)
                if not success:
                    raise RuntimeError("Inference runner returned False.")
                    
                logger.stop(success=True)
                summary["total_completed"] += 1
                
            except Exception as e:
                logger.stop(success=False, error=e)
                summary["total_failed"] += 1
                print(f"[Executor] ERROR during execution: {e}")
                
            # Save runtime log
            runtime_record = logger.get_runtime_record()
            write_json_artifact(exec_dir, "runtime.json", runtime_record)

            # ── Register Execution ────────────────────────────────────────
            record_data = {
                "execution_id": logger.execution_id,
                "experiment_id": exp_id,
                "parent_experiment": experiment.get("experiment_family", "UNKNOWN"),
                "planner_version": traceability["planner_version"],
                "reasoning_version": traceability["reasoning_version"],
                "knowledge_graph_version": traceability["knowledge_graph_version"],
                "benchmark_version": traceability["benchmark_version"],
                "dataset_version": traceability["dataset_version"],
                "executor_version": traceability["executor_version"],
                "execution_timestamp": logger.start_time if logger.start_time else time.time(),
                "execution_directory": exec_dir,
                "execution_status": logger.status,
                "artifact_manifest": "execution_manifest.json"
            }
            is_new = registry.register(record_data)
            if not is_new:
                duplicate_records += 1

            # ── Validate Execution ────────────────────────────────────────
            is_valid = validate_execution(exec_dir, execution_id=logger.execution_id, registry=registry)
            if is_valid:
                summary["total_validated"] += 1
                final_status = "VALIDATED"
            else:
                final_status = "INVALID" if logger.status == "COMPLETED" else "FAILED"
                
            # Append Record
            execution_records.append({
                "execution_id":    logger.execution_id,
                "experiment_id":   exp_id,
                "step_index":      step_idx,
                "status":          final_status,
                "execution_dir":   exec_dir,
                "duration_sec":    runtime_record["duration_sec"],
                "error_message":   logger.error_message
            })

    # ── Final Registry Validation ──────────────────────────────────────────
    registry_valid = validate_entire_registry(registry)
    if not registry_valid:
        print("[Executor] WARNING: Global registry validation failed.")

    new_records = registry.total_registered - initial_registry_count

    # ── Export Execution Report ────────────────────────────────────────────
    report = {
        "metadata": {
            "executor_version": EXECUTOR_VERSION,
            "timestamp":        timestamp,
            "plan_file":        os.path.basename(plan_path)
        },
        "summary": summary,
        "traceability_summary": {
            "total_registered": registry.total_registered,
            "new_records": new_records,
            "duplicate_records": duplicate_records,
            "registry_version": registry.version
        },
        "execution_records": execution_records
    }
    
    report_path = os.path.join(output_dir, REPORT_FILENAME)
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)
        
    print(f"\n[Executor] Pipeline finished. Report saved to {report_path}")
    return report

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="F5-TTS Experiment Executor")
    parser.add_argument("--plan", required=True, help="Path to experiment_plan.json")
    parser.add_argument("--output_dir", default="executions", help="Directory for execution output")
    args = parser.parse_args()
    
    run_executor(args.plan, args.output_dir)
