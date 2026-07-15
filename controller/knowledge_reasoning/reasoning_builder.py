"""
reasoning_builder.py
"""
import uuid
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from rule_evaluator import evaluate_rule
from conflict_resolver import resolve_conflicts
from reasoning_schema import FINDING_TYPE_NO_APPLICABLE_RULE

def build_findings(retrieval_result: dict, rule_registry: dict) -> list:
    records = retrieval_result.get("matched_records", [])
    rules = rule_registry.get("rules", [])
    findings = []
    
    for record in records:
        matched_rules = []
        for rule in rules:
            if evaluate_rule(record, rule):
                matched_rules.append(rule)
                
        winner = resolve_conflicts(matched_rules)
        record_id = record.get("learning_record_id")
        
        if winner:
            finding = {
                "finding_id": f"FND-{uuid.uuid4().hex[:8].upper()}",
                "rule_id": winner.get("rule_id"),
                "priority": winner.get("priority"),
                "finding_type": winner.get("finding_type"),
                "matched_learning_record_ids": [record_id],
                "explanation": winner.get("explanation"),
                "traceability": record.get("traceability", {})
            }
        else:
            finding = {
                "finding_id": f"FND-{uuid.uuid4().hex[:8].upper()}",
                "rule_id": "NONE",
                "priority": 0,
                "finding_type": FINDING_TYPE_NO_APPLICABLE_RULE,
                "matched_learning_record_ids": [record_id],
                "explanation": "No reasoning rule matched the criteria for this record.",
                "traceability": record.get("traceability", {})
            }
        findings.append(finding)
        
    return findings
