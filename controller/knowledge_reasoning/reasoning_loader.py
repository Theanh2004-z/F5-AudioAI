"""
reasoning_loader.py
"""
import json
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from reasoning_schema import ReasoningError, ERROR_ARTIFACT_CORRUPTED, ERROR_RULE_REGISTRY_CORRUPTED

def load_artifacts(retrieval_result_path: str, rule_registry_path: str) -> tuple:
    if not os.path.exists(retrieval_result_path):
        raise ReasoningError(ERROR_ARTIFACT_CORRUPTED, f"Retrieval result missing: {retrieval_result_path}")
    if not os.path.exists(rule_registry_path):
        raise ReasoningError(ERROR_RULE_REGISTRY_CORRUPTED, f"Rule registry missing: {rule_registry_path}")

    try:
        with open(retrieval_result_path, "r", encoding="utf-8") as f:
            retrieval_result = json.load(f)
    except Exception:
        raise ReasoningError(ERROR_ARTIFACT_CORRUPTED, "Failed to parse retrieval_result JSON")

    try:
        with open(rule_registry_path, "r", encoding="utf-8") as f:
            rule_registry = json.load(f)
    except Exception:
        raise ReasoningError(ERROR_RULE_REGISTRY_CORRUPTED, "Failed to parse rule_registry JSON")
        
    return retrieval_result, rule_registry
