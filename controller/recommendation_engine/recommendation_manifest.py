"""
recommendation_manifest.py
"""
import json
import os
import hashlib
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from recommendation_schema import RECOMMENDATION_SCHEMA_VERSION

def generate_manifest(session_id, prediction_path, rec_path, out_dir):
    def get_hash(path):
        if not os.path.exists(path): return ""
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
            
    manifest = {
        "schema_version": RECOMMENDATION_SCHEMA_VERSION,
        "recommendation_session_id": session_id,
        "prediction_checksum": get_hash(prediction_path),
        "recommendation_checksum": get_hash(rec_path)
    }
    mpath = os.path.join(out_dir, f"recommendation_manifest_{session_id}.json")
    with open(mpath, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=4)
    return manifest, mpath
