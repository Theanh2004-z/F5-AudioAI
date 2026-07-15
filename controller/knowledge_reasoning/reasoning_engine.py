"""
reasoning_engine.py
"""
import os
import sys
import uuid
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from reasoning_schema import REASONING_SCHEMA_VERSION, ReasoningError
from reasoning_loader import load_artifacts
from reasoning_builder import build_findings
from reasoning_manifest import generate_manifest
from reasoning_registry import ReasoningRegistry
from reasoning_logger import ReasoningLogger

def execute_reasoning(retrieval_result_path: str, rule_registry_path: str, output_dir: str = "dataset/reasoning") -> dict:
    """
    Consumes a retrieval result artifact and evaluates it against deterministic generic rules, producing Reasoning Findings.
    """
    logger = ReasoningLogger()
    os.makedirs(output_dir, exist_ok=True)
    registry = ReasoningRegistry(output_dir)
    
    session_id = f"RSN-{uuid.uuid4().hex[:8].upper()}"
    
    retrieval_result, rule_registry = load_artifacts(retrieval_result_path, rule_registry_path)
    
    findings = build_findings(retrieval_result, rule_registry)
    
    retrieval_session_id = retrieval_result.get("retrieval_session_id", "UNKNOWN")
    
    output = {
        "reasoning_session_id": session_id,
        "retrieval_session_id": retrieval_session_id,
        "findings": findings,
        "traceability": {
            "reasoning_pipeline_timestamp": logger.get_timestamp()
        }
    }
    
    findings_path = os.path.join(output_dir, f"reasoning_findings_{session_id}.json")
    with open(findings_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=4)
        
    manifest, manifest_path = generate_manifest(
        session_id, retrieval_result_path, rule_registry_path, findings_path, output_dir, registry.version
    )
    
    registry.register(
        session_id=session_id,
        findings_path=findings_path,
        manifest_path=manifest_path,
        status="SUCCESS",
        checksum=manifest["reasoning_findings_checksum"]
    )
    
    return output
