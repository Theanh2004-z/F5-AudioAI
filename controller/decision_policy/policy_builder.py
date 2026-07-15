"""
policy_builder.py
"""
import uuid
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from policy_evaluator import evaluate_policy_rule
from conflict_resolver import resolve_conflicts
from policy_schema import POLICY_TYPE_NO_APPLICABLE_POLICY

def build_policies(findings_data: dict, policy_registry: dict) -> list:
    findings = findings_data.get("findings", [])
    policy_rules = policy_registry.get("policy_rules", [])
    policies = []
    
    # Group findings by their matched learning records
    grouped_findings = {}
    for f in findings:
        key = tuple(sorted(f.get("matched_learning_record_ids", [])))
        if key not in grouped_findings:
            grouped_findings[key] = []
        grouped_findings[key].append(f)
        
    for key, group in grouped_findings.items():
        matched_rules = []
        rule_to_finding = {}
        for f in group:
            for rule in policy_rules:
                if evaluate_policy_rule(f, rule):
                    matched_rules.append(rule)
                    rule_id = rule.get("policy_rule_id")
                    if rule_id not in rule_to_finding:
                        rule_to_finding[rule_id] = []
                    rule_to_finding[rule_id].append(f.get("finding_id"))
                    
        winner = resolve_conflicts(matched_rules)
        all_finding_ids = [f.get("finding_id") for f in group]
        
        # Merge traceability
        merged_traceability = {}
        for f in group:
            tr = f.get("traceability", {})
            for k, v in tr.items():
                if isinstance(v, list):
                    merged_traceability.setdefault(k, []).extend(v)
                else:
                    merged_traceability[k] = v
        for k, v in merged_traceability.items():
            if isinstance(v, list):
                merged_traceability[k] = list(sorted(set(v)))
                
        if winner:
            rule_id = winner.get("policy_rule_id")
            trigger_ids = rule_to_finding.get(rule_id, all_finding_ids)
            policy = {
                "policy_id": f"POL-{uuid.uuid4().hex[:8].upper()}",
                "policy_type": winner.get("policy_type"),
                "applied_policy_rule_id": rule_id,
                "trigger_finding_ids": trigger_ids,
                "decision_rationale": f"Generated from Finding {trigger_ids[0]} using Policy Rule {rule_id}.",
                "traceability": {
                    "matched_learning_record_ids": list(key),
                    "inherited_traceability": merged_traceability
                }
            }
        else:
            policy = {
                "policy_id": f"POL-{uuid.uuid4().hex[:8].upper()}",
                "policy_type": POLICY_TYPE_NO_APPLICABLE_POLICY,
                "applied_policy_rule_id": "NONE",
                "trigger_finding_ids": all_finding_ids,
                "decision_rationale": f"No policy rule matched for Findings {all_finding_ids}.",
                "traceability": {
                    "matched_learning_record_ids": list(key),
                    "inherited_traceability": merged_traceability
                }
            }
        policies.append(policy)
        
    return policies
