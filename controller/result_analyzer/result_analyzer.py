"""
result_analyzer.py
Main Orchestrator for Stage 10 — Result Analyzer.
Processes completed benchmarks deterministically to produce analysis artifacts.
"""

import os
import sys
import json
import time
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from analyzer_schema            import ANALYZER_VERSION
from benchmark_loader           import load_pending_benchmarks
from feature_delta_calculator   import calculate_feature_deltas
from quality_summarizer         import summarize_quality
from anomaly_detector           import detect_anomalies
from analysis_registry          import AnalysisRegistry
from analysis_logger            import AnalysisLogger
from analysis_validator         import validate_analysis

REPORT_FILENAME = "analysis_report.json"

def write_json_artifact(target_dir, filename, data):
    """Writes a JSON artifact to the directory."""
    path = os.path.join(target_dir, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def get_traceability(bench_manifest_path, analysis_id, bench_id, analysis_version):
    """Extracts traceability from benchmark manifest and augments it."""
    trace = {}
    if os.path.exists(bench_manifest_path):
        with open(bench_manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
            trace = manifest.get("traceability", {})
            
    return {
        "analysis_id":             analysis_id,
        "benchmark_id":            bench_id,
        "execution_id":            trace.get("execution_id", "UNKNOWN"),
        "experiment_id":           trace.get("experiment_id", "UNKNOWN"),
        "planner_version":         trace.get("planner_version", "UNKNOWN"),
        "reasoning_version":       trace.get("reasoning_version", "UNKNOWN"),
        "executor_version":        trace.get("executor_version", "UNKNOWN"),
        "benchmark_version":       trace.get("benchmark_version", "UNKNOWN"),
        "analysis_version":        analysis_version
    }

def run_result_analyzer(bench_registry_path, output_dir="analysis", reference_feature_vector=None):
    """
    Runs the Result Analyzer pipeline.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs(output_dir, exist_ok=True)
    
    registry = AnalysisRegistry(registry_dir=output_dir)
    
    # ── 1. Load Benchmarks ──────────────────────────────────────────────────
    pending_benchmarks = load_pending_benchmarks(
        bench_registry_path, registry.registry_path
    )
    
    summary = {
        "total_benchmarks_loaded": len(pending_benchmarks),
        "total_analysis_attempted": 0,
        "total_completed": 0,
        "total_failed": 0,
        "total_validated": 0
    }
    
    analysis_records = []
    
    # ── 2. Processing Loop ─────────────────────────────────────────────────
    for bench_record in pending_benchmarks:
        bench_id = bench_record["benchmark_id"]
        bench_dir = bench_record["benchmark_directory"]
        bench_manifest = os.path.join(bench_dir, "benchmark_manifest.json")
        
        summary["total_analysis_attempted"] += 1
        
        logger = AnalysisLogger(bench_id, analysis_version=ANALYZER_VERSION)
        analysis_dir = os.path.join(output_dir, logger.analysis_id)
        os.makedirs(analysis_dir, exist_ok=True)
        
        print(f"\n[Analyzer] Starting analysis for benchmark {bench_id} → {analysis_dir}")
        
        try:
            logger.start()
            
            # ── Calculate Deltas ──────────────────────────────────────────
            feature_deltas = calculate_feature_deltas(bench_dir, reference_feature_vector)
            
            # ── Summarize Quality ─────────────────────────────────────────
            quality_sum = summarize_quality(bench_dir)
            
            # ── Detect Anomalies ──────────────────────────────────────────
            anomalies = detect_anomalies(feature_deltas, quality_sum)
            
            # ── Consolidate Analysis ──────────────────────────────────────
            analysis_data = {
                "benchmark_id": bench_id,
                "anomalies_detected": anomalies,
                "summary": {
                    "vector_size": feature_deltas["vector_size"],
                    "metrics_count": quality_sum["extracted_metrics_count"]
                }
            }
            
            logger.stop(success=True)
            summary["total_completed"] += 1
            
        except Exception as e:
            logger.stop(success=False, error=e)
            summary["total_failed"] += 1
            print(f"[Analyzer] ERROR during analysis: {e}")
            feature_deltas = {}
            quality_sum = {}
            analysis_data = {"error": str(e)}
            
        # ── Save Artifacts ────────────────────────────────────────────────
        write_json_artifact(analysis_dir, "feature_delta.json", feature_deltas)
        write_json_artifact(analysis_dir, "quality_summary.json", quality_sum)
        write_json_artifact(analysis_dir, "analysis.json", analysis_data)
        
        runtime_record = logger.get_runtime_record()
        write_json_artifact(analysis_dir, "runtime.json", runtime_record)
        
        traceability = get_traceability(
            bench_manifest, logger.analysis_id, bench_id, logger.analysis_version
        )
        
        manifest = {
            "analysis_id": logger.analysis_id,
            "benchmark_id": bench_id,
            "execution_id": traceability["execution_id"],
            "experiment_id": traceability["experiment_id"],
            "timestamp": logger.start_time if logger.start_time else time.time(),
            "analyzer_version": ANALYZER_VERSION,
            "traceability": traceability
        }
        write_json_artifact(analysis_dir, "analysis_manifest.json", manifest)
        
        # ── Update Analysis Registry ──────────────────────────────────────
        reg_record = {
            "analysis_id": logger.analysis_id,
            "benchmark_id": bench_id,
            "execution_id": traceability["execution_id"],
            "experiment_id": traceability["experiment_id"],
            "analysis_timestamp": logger.start_time if logger.start_time else time.time(),
            "analysis_directory": analysis_dir,
            "analysis_status": logger.status,
            "analysis_version": logger.analysis_version
        }
        registry.register(reg_record)
        
        # ── Validate ──────────────────────────────────────────────────────
        is_valid = validate_analysis(analysis_dir, logger.analysis_id, registry)
        if is_valid:
            summary["total_validated"] += 1
            final_status = "VALIDATED"
        else:
            final_status = "INVALID" if logger.status == "COMPLETED" else "FAILED"
            
        analysis_records.append({
            "analysis_id": logger.analysis_id,
            "benchmark_id": bench_id,
            "status": final_status,
            "analysis_dir": analysis_dir,
            "duration_sec": runtime_record["duration_sec"],
            "error_message": logger.error_message
        })
        
    # ── Export Report ─────────────────────────────────────────────────────
    report = {
        "metadata": {
            "analyzer_version": ANALYZER_VERSION,
            "timestamp": timestamp,
            "benchmark_registry_file": os.path.basename(bench_registry_path)
        },
        "summary": summary,
        "analysis_records": analysis_records
    }
    
    report_path = os.path.join(output_dir, REPORT_FILENAME)
    write_json_artifact(output_dir, REPORT_FILENAME, report)
    
    print(f"\n[Analyzer] Pipeline finished. Report saved to {report_path}")
    return report

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="F5-TTS Result Analyzer")
    parser.add_argument("--bench_registry", required=True, help="Path to benchmark_registry.json")
    parser.add_argument("--output_dir", default="analysis", help="Output directory")
    parser.add_argument("--reference_features", default=None, help="Path to reference feature_vector.npy")
    args = parser.parse_args()
    
    run_result_analyzer(args.bench_registry, args.output_dir, args.reference_features)
