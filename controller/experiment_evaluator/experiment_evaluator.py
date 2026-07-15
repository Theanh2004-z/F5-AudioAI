"""
experiment_evaluator.py
Main Orchestrator for Stage 11 — Experiment Evaluator.
Evaluates the quality of experiments based on deterministic rules.
"""

import os
import sys
import json
import time
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from evaluator_schema           import EVALUATOR_VERSION
from analysis_loader            import load_pending_analyses
from experiment_comparator      import compare_features
from quality_evaluator          import evaluate_quality
from rule_evaluator             import evaluate_decision
from evaluation_profile         import generate_evaluation_profile, EVALUATION_PROFILE_VERSION
from decision_explainer         import generate_decision_explanation, DECISION_EXPLAINER_VERSION
from evaluation_statistics      import generate_evaluation_statistics
from feature_profile_registry   import FEATURE_PROFILE_VERSION
from decision_trace             import generate_decision_trace
from rule_statistics            import generate_rule_statistics
from rule_registry              import RULE_ENGINE_VERSION, RULE_REGISTRY_VERSION
from baseline_registry          import BaselineRegistry
from evaluation_registry        import EvaluationRegistry
from evaluation_logger          import EvaluationLogger
from evaluation_validator       import validate_evaluation

REPORT_FILENAME = "evaluation_report.json"

def write_json_artifact(target_dir, filename, data):
    """Writes a JSON artifact to the directory."""
    path = os.path.join(target_dir, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def get_traceability(analysis_manifest_path, eval_id, analysis_id, eval_version, baseline=None):
    """Extracts traceability from analysis manifest and augments it."""
    if baseline is None:
        baseline = {}
    trace = {}
    if os.path.exists(analysis_manifest_path):
        with open(analysis_manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
            trace = manifest.get("traceability", {})
            
    return {
        "evaluation_id":           eval_id,
        "analysis_id":             analysis_id,
        "benchmark_id":            trace.get("benchmark_id", "UNKNOWN"),
        "execution_id":            trace.get("execution_id", "UNKNOWN"),
        "experiment_id":           trace.get("experiment_id", "UNKNOWN"),
        "planner_version":         trace.get("planner_version", "UNKNOWN"),
        "reasoning_version":       trace.get("reasoning_version", "UNKNOWN"),
        "executor_version":        trace.get("executor_version", "UNKNOWN"),
        "benchmark_version":       trace.get("benchmark_version", "UNKNOWN"),
        "analysis_version":        trace.get("analysis_version", "UNKNOWN"),
        "evaluation_version":      eval_version,
        "evaluation_profile_version": EVALUATION_PROFILE_VERSION,
        "feature_registry_version": FEATURE_PROFILE_VERSION,
        "decision_explainer_version": DECISION_EXPLAINER_VERSION,
        "baseline_id":             baseline.get("baseline_id", "UNKNOWN"),
        "baseline_version":        baseline.get("baseline_version", "UNKNOWN"),
        "rule_engine_version":     RULE_ENGINE_VERSION,
        "rule_registry_version":   RULE_REGISTRY_VERSION
    }

def run_experiment_evaluator(analysis_registry_path, output_dir="evaluation"):
    """
    Runs the Experiment Evaluator pipeline.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs(output_dir, exist_ok=True)
    
    registry          = EvaluationRegistry(registry_dir=output_dir)
    baseline_registry = BaselineRegistry(registry_dir=output_dir)
    active_baseline   = baseline_registry.get_active_baseline()
    
    # ── 1. Load Analyses ────────────────────────────────────────────────────
    pending_analyses = load_pending_analyses(
        analysis_registry_path, registry.registry_path
    )
    
    summary = {
        "total_analyses_loaded": len(pending_analyses),
        "total_evaluations_attempted": 0,
        "total_completed": 0,
        "total_failed": 0,
        "total_validated": 0
    }
    
    evaluation_records = []
    
    # ── 2. Processing Loop ─────────────────────────────────────────────────
    for analysis_record in pending_analyses:
        analysis_id = analysis_record["analysis_id"]
        analysis_dir = analysis_record["analysis_directory"]
        analysis_manifest = os.path.join(analysis_dir, "analysis_manifest.json")
        
        summary["total_evaluations_attempted"] += 1
        
        logger = EvaluationLogger(analysis_id, evaluation_version=EVALUATOR_VERSION)
        eval_dir = os.path.join(output_dir, logger.evaluation_id)
        os.makedirs(eval_dir, exist_ok=True)
        
        print(f"\n[Evaluator] Starting evaluation for analysis {analysis_id} -> {eval_dir}")
        
        try:
            logger.start()
            
            # Load analysis data to get anomalies
            analysis_data_path = os.path.join(analysis_dir, "analysis.json")
            if not os.path.exists(analysis_data_path):
                raise FileNotFoundError(f"Missing {analysis_data_path}")
            with open(analysis_data_path, "r", encoding="utf-8") as f:
                analysis_data = json.load(f)
                
            # ── Compare Features ──────────────────────────────────────────
            comparisons = compare_features(analysis_dir)
            
            # ── Evaluate Quality ──────────────────────────────────────────
            quality_evals = evaluate_quality(comparisons, analysis_data)
            
            # ── Generate Evaluation Profile ───────────────────────────────
            profile = generate_evaluation_profile(quality_evals)
            
            # ── Evaluate Rules ────────────────────────────────────────────
            decision = evaluate_decision(quality_evals, analysis_data)
            
            # -- Generate Decision Trace ----------------------------------------
            trace_records = generate_decision_trace(quality_evals, analysis_data)
            
            # -- Generate Rule Statistics ---------------------------------------
            rule_stats = generate_rule_statistics(trace_records)
            
            # -- Explain Decision -----------------------------------------------
            explanation = generate_decision_explanation(decision, profile, analysis_data)
            
            # -- Generate Evaluation Statistics ---------------------------------
            stats = generate_evaluation_statistics(decision, profile)
            
            logger.stop(success=True)
            summary["total_completed"] += 1
            
        except Exception as e:
            logger.stop(success=False, error=e)
            summary["total_failed"] += 1
            print(f"[Evaluator] ERROR during evaluation: {e}")
            comparisons   = []
            quality_evals = []
            profile       = {}
            explanation   = {}
            trace_records = []
            rule_stats    = {}
            stats         = {}
            decision      = "INVALID"
            
        # ── Save Artifacts ────────────────────────────────────────────────
        write_json_artifact(eval_dir, "evaluation.json", {"feature_comparisons": comparisons})
        write_json_artifact(eval_dir, "scorecard.json", {"feature_evaluations": quality_evals})
        write_json_artifact(eval_dir, "decision.json", {"final_decision": decision})
        write_json_artifact(eval_dir, "evaluation_profile.json", profile)
        write_json_artifact(eval_dir, "decision_explanation.json", explanation)
        write_json_artifact(eval_dir, "decision_trace.json", {"trace": trace_records})
        write_json_artifact(eval_dir, "rule_statistics.json", rule_stats)
        write_json_artifact(eval_dir, "evaluation_statistics.json", stats)
        
        runtime_record = logger.get_runtime_record()
        write_json_artifact(eval_dir, "runtime.json", runtime_record)
        
        traceability = get_traceability(
            analysis_manifest, logger.evaluation_id, analysis_id, logger.evaluation_version,
            baseline=active_baseline
        )
        
        manifest = {
            "evaluation_id": logger.evaluation_id,
            "analysis_id": analysis_id,
            "experiment_id": traceability["experiment_id"],
            "timestamp": logger.start_time if logger.start_time else time.time(),
            "evaluator_version": EVALUATOR_VERSION,
            "traceability": traceability
        }
        write_json_artifact(eval_dir, "evaluation_manifest.json", manifest)
        
        # ── Update Evaluation Registry ──────────────────────────────────────
        reg_record = {
            "evaluation_id": logger.evaluation_id,
            "analysis_id": analysis_id,
            "benchmark_id": traceability["benchmark_id"],
            "execution_id": traceability["execution_id"],
            "experiment_id": traceability["experiment_id"],
            "evaluation_timestamp": logger.start_time if logger.start_time else time.time(),
            "evaluation_directory": eval_dir,
            "evaluation_status": logger.status,
            "evaluation_version": logger.evaluation_version,
            "decision": decision
        }
        registry.register(reg_record)
        
        # ── Validate ──────────────────────────────────────────────────────
        is_valid = validate_evaluation(eval_dir, logger.evaluation_id, registry)
        if is_valid:
            summary["total_validated"] += 1
            final_status = "VALIDATED"
        else:
            final_status = "INVALID" if logger.status == "COMPLETED" else "FAILED"
            
        evaluation_records.append({
            "evaluation_id": logger.evaluation_id,
            "analysis_id": analysis_id,
            "status": final_status,
            "decision": decision,
            "evaluation_dir": eval_dir,
            "duration_sec": runtime_record["duration_sec"],
            "error_message": logger.error_message
        })
        
    # ── Export Report ─────────────────────────────────────────────────────
    report = {
        "metadata": {
            "evaluator_version": EVALUATOR_VERSION,
            "timestamp": timestamp,
            "analysis_registry_file": os.path.basename(analysis_registry_path)
        },
        "summary": summary,
        "evaluation_records": evaluation_records
    }
    
    report_path = os.path.join(output_dir, REPORT_FILENAME)
    write_json_artifact(output_dir, REPORT_FILENAME, report)
    
    print(f"\n[Evaluator] Pipeline finished. Report saved to {report_path}")
    return report

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="F5-TTS Experiment Evaluator")
    parser.add_argument("--analysis_registry", required=True, help="Path to analysis_registry.json")
    parser.add_argument("--output_dir", default="evaluation", help="Output directory")
    args = parser.parse_args()
    
    run_experiment_evaluator(args.analysis_registry, args.output_dir)
