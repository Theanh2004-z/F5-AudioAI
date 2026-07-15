"""
decision_policy_engine.py
"""
import os
import sys
import uuid
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from policy_schema import POLICY_SCHEMA_VERSION, PolicyError
from policy_loader import load_artifacts
from policy_builder import build_policies
from policy_manifest import generate_manifest
from policy_registry import PolicyRegistry
from policy_logger import PolicyLogger

def build_decision_policy(reasoning_findings_path: str, policy_registry_path: str, output_dir: str = "dataset/policy") -> dict:
    """
    Transforms reasoning findings into deterministic system policies based on a static rule registry.
    """
    logger = PolicyLogger()
    os.makedirs(output_dir, exist_ok=True)
    registry = PolicyRegistry(output_dir)
    
    session_id = f"POL-{uuid.uuid4().hex[:8].upper()}"
    
    findings_data, policy_registry = load_artifacts(reasoning_findings_path, policy_registry_path)
    
    policies = build_policies(findings_data, policy_registry)
    
    reasoning_session_id = findings_data.get("reasoning_session_id", "UNKNOWN")
    
    output = {
        "policy_session_id": session_id,
        "reasoning_session_id": reasoning_session_id,
        "policies": policies,
        "traceability": {
            "policy_pipeline_timestamp": logger.get_timestamp()
        }
    }
    
    policy_path = os.path.join(output_dir, f"decision_policies_{session_id}.json")
    with open(policy_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=4)
        
    manifest, manifest_path = generate_manifest(
        session_id, reasoning_findings_path, policy_registry_path, policy_path, output_dir, registry.version
    )
    
    registry.register(
        session_id=session_id,
        policy_path=policy_path,
        manifest_path=manifest_path,
        status="SUCCESS",
        checksum=manifest["decision_policy_checksum"]
    )
    
    return output
