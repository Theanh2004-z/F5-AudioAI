"""
knowledge_consistency.py
Runs deterministic consistency checks across the knowledge base.
No AI, no inference. Pattern-matching and cross-reference checks only.
Produces knowledge_consistency.json.
"""

import json
import os

KNOWLEDGE_CONSISTENCY_FILENAME = "knowledge_consistency.json"

def run_consistency_checks(knowledge_base_levers, knowledge_registry, base_dir="knowledge"):
    """
    Validates internal consistency of the knowledge base.
    
    Args:
        knowledge_base_levers: dict from KnowledgeBase.get_all_levers()
        knowledge_registry: KnowledgeRegistry instance.
        base_dir: Output directory.
        
    Returns:
        dict: Consistency report.
    """
    issues = []
    checks = {
        "duplicate_experiment_ids": {"passed": True, "detail": []},
        "missing_traceability":     {"passed": True, "detail": []},
        "broken_evidence_chain":    {"passed": True, "detail": []},
        "invalid_references":       {"passed": True, "detail": []},
        "orphan_knowledge":         {"passed": True, "detail": []}
    }

    # Build known sets from registry
    registry_knowledge_ids = {r["knowledge_id"] for r in knowledge_registry._registry.get("records", [])}
    registry_eval_ids      = {r["evaluation_id"]  for r in knowledge_registry._registry.get("records", [])}

    # CHECK 1: Duplicate experiment IDs across levers
    all_exp_ids = []
    for lever, data in knowledge_base_levers.items():
        all_exp_ids.extend(data.get("supporting_experiments", []))
    seen_exp = set()
    duplicates = set()
    for eid in all_exp_ids:
        if eid in seen_exp:
            duplicates.add(eid)
        seen_exp.add(eid)
    if duplicates:
        checks["duplicate_experiment_ids"]["passed"] = False
        checks["duplicate_experiment_ids"]["detail"] = list(duplicates)
        issues.append(f"Duplicate experiment IDs: {list(duplicates)}")

    # CHECK 2: Missing traceability (knowledge dirs without manifest)
    for record in knowledge_registry._registry.get("records", []):
        kdir    = record.get("knowledge_directory", "")
        k_id    = record.get("knowledge_id", "")
        mpath   = os.path.join(kdir, "knowledge_manifest.json")
        if kdir and not os.path.exists(mpath):
            checks["missing_traceability"]["passed"] = False
            checks["missing_traceability"]["detail"].append(k_id)
            issues.append(f"Missing manifest for {k_id}")

    # CHECK 3: Broken evidence chain (supporting_evaluations ref unknown eval IDs)
    for lever, data in knowledge_base_levers.items():
        for eval_entry in data.get("supporting_evaluations", []):
            eid = eval_entry.get("evaluation_id", "")
            if eid not in registry_eval_ids:
                checks["broken_evidence_chain"]["passed"] = False
                checks["broken_evidence_chain"]["detail"].append(eid)
                issues.append(f"Broken evidence chain: {eid} not in registry")

    # CHECK 4: Invalid references (knowledge_ids in base not matching registry)
    for lever, data in knowledge_base_levers.items():
        for kid in data.get("knowledge_ids", []):
            if kid not in registry_knowledge_ids:
                checks["invalid_references"]["passed"] = False
                checks["invalid_references"]["detail"].append(kid)
                issues.append(f"Invalid reference: {kid} not in registry")

    # CHECK 5: Orphan knowledge (in registry but not assigned to any lever)
    base_knowledge_ids = set()
    for lever, data in knowledge_base_levers.items():
        base_knowledge_ids.update(data.get("knowledge_ids", []))
    for kid in registry_knowledge_ids:
        if kid not in base_knowledge_ids:
            checks["orphan_knowledge"]["passed"] = False
            checks["orphan_knowledge"]["detail"].append(kid)
            issues.append(f"Orphan knowledge: {kid}")

    total_issues   = len(issues)
    overall_passed = total_issues == 0

    result = {
        "overall_passed":   overall_passed,
        "total_issues":     total_issues,
        "issues":           issues,
        "checks":           checks
    }

    out_path = os.path.join(base_dir, KNOWLEDGE_CONSISTENCY_FILENAME)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4)

    status = "PASS" if overall_passed else "FAIL"
    print(f"[KnowledgeConsistency] {status} — {total_issues} issue(s) found.")
    return result
