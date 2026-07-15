"""
policy_manifest.py
"""
import json
import os
import hashlib
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from policy_schema import POLICY_SCHEMA_VERSION

def generate_manifest(session_id: str, findings_path: str, registry_path: str, output_policy_path: str, output_dir: str, registry_version: str) -> dict:
    with open(findings_path, "rb") as f:
        findings_checksum = hashlib.sha256(f.read()).hexdigest()
    with open(registry_path, "rb") as f:
        registry_checksum = hashlib.sha256(f.read()).hexdigest()
    with open(output_policy_path, "rb") as f:
        policy_checksum = hashlib.sha256(f.read()).hexdigest()
        
    manifest = {
        "schema_version": POLICY_SCHEMA_VERSION,
        "policy_session_id": session_id,
        "reasoning_findings_checksum": findings_checksum,
        "policy_registry_checksum": registry_checksum,
        "decision_policy_checksum": policy_checksum,
        "registry_version": registry_version
    }
    
    manifest_path = os.path.join(output_dir, f"decision_policy_manifest_{session_id}.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=4)
        
    return manifest, manifest_path
