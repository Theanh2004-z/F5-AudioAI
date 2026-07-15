"""
report_generator.py
Generates the strict auditable metrics report.
"""
import json
import os

def generate_report(stats, output_dir):
    report = {
        "report_id": stats["report_id"],
        "source_dataset_version": stats["source_dataset_version"],
        "execution_time": stats["execution_time"],
        "total_samples": stats["total_samples"],
        "valid_samples": stats["valid_samples"],
        "invalid_samples": stats["invalid_samples"],
        "duplicate_samples": stats["duplicate_samples"],
        "corrupted_samples": stats["corrupted_samples"],
        "incomplete_samples": stats["incomplete_samples"],
        "quality_ratio": round(stats["valid_samples"] / max(1, stats["total_samples"]), 4),
        "rule_statistics": stats["rule_statistics"],
        "triggered_rule_ids": sorted(list(stats["triggered_rule_ids"])),
        "skipped_rule_ids": sorted(list(stats["skipped_rule_ids"]))
    }
    path = os.path.join(output_dir, "curation_quality_report.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)
    return report
