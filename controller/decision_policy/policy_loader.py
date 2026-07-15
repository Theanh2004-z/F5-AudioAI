"""
policy_loader.py
"""
import json
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from policy_schema import PolicyError, ERROR_ARTIFACT_CORRUPTED, ERROR_POLICY_REGISTRY_CORRUPTED

def load_artifacts(reasoning_findings_path: str, policy_registry_path: str) -> tuple:
    if not os.path.exists(reasoning_findings_path):
        raise PolicyError(ERROR_ARTIFACT_CORRUPTED, f"Reasoning findings missing: {reasoning_findings_path}")
    if not os.path.exists(policy_registry_path):
        raise PolicyError(ERROR_POLICY_REGISTRY_CORRUPTED, f"Policy registry missing: {policy_registry_path}")

    try:
        with open(reasoning_findings_path, "r", encoding="utf-8") as f:
            findings_data = json.load(f)
    except Exception:
        raise PolicyError(ERROR_ARTIFACT_CORRUPTED, "Failed to parse reasoning_findings JSON")

    try:
        with open(policy_registry_path, "r", encoding="utf-8") as f:
            policy_registry = json.load(f)
    except Exception:
        raise PolicyError(ERROR_POLICY_REGISTRY_CORRUPTED, "Failed to parse policy_registry JSON")
        
    return findings_data, policy_registry
