"""
dataset_curation_engine.py
The ONLY public API orchestrator.
"""
import os
import sys
import uuid
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from dataset_loader import load_source_dataset
from schema_validator import check_schema_version
from corruption_detector import check_corruption
from duplicate_detector import check_duplicate
from quarantine_manager import add_to_quarantine, export_quarantine
from report_generator import generate_report
from manifest_validator import generate_and_validate_manifest
from curation_registry import CurationRegistry
from curation_logger import CurationLogger
from curation_validator import validate_curation
from curation_rule_registry import RULES
from curation_schema import CURATION_SCHEMA_VERSION

def curate_dataset(stage13_registry_path, output_dir="dataset/curated"):
    logger = CurationLogger()
    os.makedirs(output_dir, exist_ok=True)
    registry = CurationRegistry(output_dir)
    
    # 1. Load Data
    raw_samples, source_metadata = load_source_dataset(stage13_registry_path)
    
    curated_samples = []
    quarantine_records = []
    seen_ids = set()
    
    stats = {
        "report_id": f"CUR-REP-{uuid.uuid4().hex[:6].upper()}",
        "source_dataset_version": source_metadata.get("dataset_version", "1.0.0"),
        "total_samples": len(raw_samples),
        "valid_samples": 0,
        "invalid_samples": 0,
        "duplicate_samples": 0,
        "corrupted_samples": 0,
        "incomplete_samples": 0,
        "rule_statistics": {r: 0 for r in RULES},
        "triggered_rule_ids": set(),
        "skipped_rule_ids": set()
    }
    
    # 2. Inspect & Classify
    for sample in raw_samples:
        reasons = []
        status = "VALID"
        
        # Schema Version Check
        s_ok, s_rs = check_schema_version(sample, "1.0.0") 
        if not s_ok:
            reasons.extend(s_rs)
            status = "INVALID_SCHEMA"
            stats["invalid_samples"] += 1
            
        # Duplicate Check
        d_ok, d_rs = check_duplicate(sample, seen_ids)
        if not d_ok:
            reasons.extend(d_rs)
            if status == "VALID":
                status = "DUPLICATE_ID"
                stats["duplicate_samples"] += 1
                
        # Corruption Check
        c_ok, c_rs = check_corruption(sample)
        if not c_ok:
            reasons.extend(c_rs)
            if status == "VALID":
                if "RULE-001" in c_rs:
                    status = "INCOMPLETE"
                    stats["incomplete_samples"] += 1
                else:
                    status = "CORRUPTED"
                    stats["corrupted_samples"] += 1
                    
        # Tally Rules
        for r in reasons:
            stats["rule_statistics"][r] += 1
            stats["triggered_rule_ids"].add(r)
            
        if status == "VALID":
            curated_samples.append(sample)
            stats["valid_samples"] += 1
        else:
            q_rec = add_to_quarantine(sample, reasons, status)
            quarantine_records.append(q_rec)
            
    # Calculate skipped rules
    for r in RULES:
        if r not in stats["triggered_rule_ids"]:
            stats["skipped_rule_ids"].add(r)
            
    stats["execution_time"] = logger.duration()
    
    # 3. Export Valid Dataset
    dataset_version = source_metadata.get("dataset_version", "1.0.0")
    dataset_filename = f"curated_dataset_v{dataset_version}.json"
    dataset_path = os.path.join(output_dir, dataset_filename)
    
    with open(dataset_path, "w", encoding="utf-8") as f:
        json.dump(curated_samples, f, indent=4)
        
    # 4. Export Quarantine
    export_quarantine(quarantine_records, output_dir)
    
    # 5. Export Report
    generate_report(stats, output_dir)
    
    # 6. Generate Manifest
    source_id = source_metadata.get("dataset_id", "UNKNOWN")
    manifest = generate_and_validate_manifest(
        curated_samples, source_id, dataset_version, dataset_path, source_id, output_dir
    )
    
    # 7. Register
    reg_entry = {
        "dataset_id": manifest["curated_dataset_id"],
        "dataset_version": dataset_version,
        "dataset_path": dataset_filename,
        "manifest_path": "curated_manifest.json",
        "checksum": manifest["checksum"],
        "total_samples": manifest["total_samples"],
        "status": "CURATED"
    }
    registry.register(reg_entry)
    
    # 8. Final Validation Check
    is_valid = validate_curation(manifest, reg_entry)
    if not is_valid:
        raise RuntimeError("Curated Manifest Validation Failed!")
        
    return manifest
    
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", required=True)
    parser.add_argument("--output_dir", default="dataset/curated")
    args = parser.parse_args()
    curate_dataset(args.registry, args.output_dir)
