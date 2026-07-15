"""
reasoning_manifest.py
"""
import json
import os
import hashlib
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from reasoning_schema import REASONING_SCHEMA_VERSION

def generate_manifest(session_id: str, result_path: str, rule_registry_path: str, output_findings_path: str, output_dir: str, registry_version: str) -> dict:
    with open(result_path, "rb") as f:
        retrieval_checksum = hashlib.sha256(f.read()).hexdigest()
    with open(rule_registry_path, "rb") as f:
        rule_registry_checksum = hashlib.sha256(f.read()).hexdigest()
    with open(output_findings_path, "rb") as f:
        findings_checksum = hashlib.sha256(f.read()).hexdigest()
        
    manifest = {
        "schema_version": REASONING_SCHEMA_VERSION,
        "reasoning_session_id": session_id,
        "retrieval_result_checksum": retrieval_checksum,
        "rule_registry_checksum": rule_registry_checksum,
        "reasoning_findings_checksum": findings_checksum,
        "registry_version": registry_version
    }
    
    manifest_path = os.path.join(output_dir, f"reasoning_manifest_{session_id}.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=4)
        
    return manifest, manifest_path
