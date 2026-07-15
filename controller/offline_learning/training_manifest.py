"""
training_manifest.py
"""
import json
import os
import hashlib
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from learning_schema import LEARNING_SCHEMA_VERSION

def generate_manifest(session_id, ds_path, rsn_path, pol_path, models_dir, out_dir):
    def get_hash(path):
        if not os.path.exists(path): return ""
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
            
    manifest = {
        "schema_version": LEARNING_SCHEMA_VERSION,
        "learning_session_id": session_id,
        "learning_dataset_checksum": get_hash(ds_path),
        "reasoning_findings_checksum": get_hash(rsn_path),
        "decision_policy_checksum": get_hash(pol_path),
        "production_model_checksum": get_hash(os.path.join(models_dir, "production_model.pkl"))
    }
    mpath = os.path.join(out_dir, f"training_manifest_{session_id}.json")
    with open(mpath, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=4)
    return manifest, mpath
