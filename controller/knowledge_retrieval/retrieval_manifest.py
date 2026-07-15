"""
retrieval_manifest.py
"""
import json
import os
import hashlib
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from retrieval_schema import RETRIEVAL_SCHEMA_VERSION

def generate_manifest(session_id: str, query_path: str, result_path: str, output_dir: str, registry_version: str) -> dict:
    """Generates dual-checksum manifest."""
    with open(query_path, "rb") as f:
        query_checksum = hashlib.sha256(f.read()).hexdigest()
        
    with open(result_path, "rb") as f:
        result_checksum = hashlib.sha256(f.read()).hexdigest()
        
    manifest = {
        "schema_version": RETRIEVAL_SCHEMA_VERSION,
        "retrieval_session_id": session_id,
        "query_checksum": query_checksum,
        "result_checksum": result_checksum,
        "registry_version": registry_version
    }
    
    manifest_path = os.path.join(output_dir, f"retrieval_manifest_{session_id}.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=4)
        
    return manifest, manifest_path
