"""
knowledge_validator.py
Validates that all expected artifacts exist in a knowledge directory.
Also validates global knowledge base artifacts.
Returns PASS or FAIL only. No quality evaluation.
"""

import os
import json
from knowledge_schema import EXPECTED_ARTIFACTS
from graph_validator import validate_graph_file

# Global artifacts that must exist at the base directory level
GLOBAL_ARTIFACTS = [
    "knowledge_base.json",
    "knowledge_index.json",
    "knowledge_global_statistics.json",
    "knowledge_consistency.json",
    "knowledge_snapshot.json",
    "knowledge_graph.json",
    "knowledge_graph_index.json",
    "knowledge_graph_statistics.json"
]

# Required traceability fields per record manifest
REQUIRED_TRACEABILITY = [
    "knowledge_id", "evaluation_id", "analysis_id",
    "benchmark_id", "execution_id", "experiment_id",
    "baseline_id", "planner_version", "reasoning_version",
    "executor_version", "benchmark_version", "analysis_version",
    "evaluation_version", "knowledge_builder_version",
    "knowledge_base_version", "knowledge_statistics_version",
    "knowledge_snapshot_version", "knowledge_index_version"
]

def validate_knowledge(knowledge_dir, knowledge_id, registry):
    """
    Validates per-record artifacts, registry entry, and traceability.
    """
    if not os.path.exists(knowledge_dir):
        print(f"[KnowledgeValidator] FAIL: Directory missing {knowledge_dir}")
        return False

    for artifact in EXPECTED_ARTIFACTS:
        path = os.path.join(knowledge_dir, artifact)
        if not os.path.exists(path):
            print(f"[KnowledgeValidator] FAIL: Missing artifact '{artifact}' in {knowledge_dir}")
            return False

    found = any(r["knowledge_id"] == knowledge_id for r in registry._registry.get("records", []))
    if not found:
        print(f"[KnowledgeValidator] FAIL: {knowledge_id} missing from registry.")
        return False

    manifest_path = os.path.join(knowledge_dir, "knowledge_manifest.json")
    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
        trace = manifest.get("traceability", {})
        for field in REQUIRED_TRACEABILITY:
            if field not in trace:
                print(f"[KnowledgeValidator] FAIL: Missing '{field}' in traceability.")
                return False
    except Exception as e:
        print(f"[KnowledgeValidator] FAIL: Could not read manifest: {e}")
        return False

    print(f"[KnowledgeValidator] PASS: {knowledge_dir}")
    return True


def validate_global_artifacts(base_dir):
    """
    Validates that all global knowledge base files exist and are valid.
    """
    all_pass = True
    for fname in GLOBAL_ARTIFACTS:
        path = os.path.join(base_dir, fname)
        if not os.path.exists(path):
            print(f"[KnowledgeValidator] FAIL (global): Missing '{fname}' in {base_dir}")
            all_pass = False

    # Structural validation of the knowledge graph
    graph_path = os.path.join(base_dir, "knowledge_graph.json")
    if os.path.exists(graph_path):
        res = validate_graph_file(graph_path)
        if not res["is_valid"]:
            print(f"[KnowledgeValidator] FAIL (global): knowledge_graph.json validation failed.")
            for err in res["errors"]:
                print(f"  - {err}")
            all_pass = False
        else:
            print("[KnowledgeValidator] PASS (global): knowledge_graph.json structural validation passed.")

    if all_pass:
        print(f"[KnowledgeValidator] PASS (global): All global artifacts present and validated.")
    return all_pass
