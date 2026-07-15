"""
quality_summarizer.py
Extracts and summarizes quality metrics from the benchmark report.
No scoring or ranking.
"""

import os
import json

def summarize_quality(benchmark_dir):
    """
    Reads the benchmark report.json and summarizes the raw metrics.
    
    Args:
        benchmark_dir: Path to the benchmark artifacts folder.
        
    Returns:
        dict: A summary dictionary of quality metrics.
    """
    report_path = os.path.join(benchmark_dir, "report.json")
    
    if not os.path.exists(report_path):
        raise FileNotFoundError(f"[QualitySummarizer] report.json not found in {benchmark_dir}")
        
    with open(report_path, "r", encoding="utf-8") as f:
        report = json.load(f)
        
    metrics = report.get("metrics", {})
    
    # We simply map and summarize what exists. We do not invent scores.
    summary = {
        "extracted_metrics_count": len(metrics),
        "raw_metrics": metrics,
        "status_flag": report.get("status", "UNKNOWN")
    }
    
    return summary
