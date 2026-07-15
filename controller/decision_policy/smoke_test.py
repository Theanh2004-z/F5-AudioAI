"""
smoke_test.py
"""
import os
import sys
import json
import shutil
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from decision_policy_engine import build_decision_policy
from policy_schema import PolicyError, POLICY_TYPE_NO_APPLICABLE_POLICY

class TestDecisionPolicyEngine(unittest.TestCase):
    def setUp(self):
        self.output_dir = "test_policy_output"
        self.mock_findings = "test_reasoning_findings.json"
        self.mock_registry = "test_policy_rule_registry.json"
        
        os.makedirs(self.output_dir, exist_ok=True)
        
        findings_data = {
            "reasoning_session_id": "RSN-TEST",
            "findings": [
                {
                    "finding_id": "FND-1",
                    "finding_type": "EVIDENCE_HIGH_SUPPORT",
                    "matched_learning_record_ids": ["LRN-1"],
                    "traceability": {"source_sample_ids": ["S1"]}
                },
                {
                    "finding_id": "FND-2",
                    "finding_type": "CONFLICT_PRESENT",
                    "matched_learning_record_ids": ["LRN-1"],
                    "traceability": {"source_sample_ids": ["S1", "S2"]}
                },
                {
                    "finding_id": "FND-3",
                    "finding_type": "WEIRD_EVIDENCE",
                    "matched_learning_record_ids": ["LRN-2"],
                    "traceability": {"source_sample_ids": ["S3"]}
                }
            ]
        }
        with open(self.mock_findings, "w", encoding="utf-8") as f:
            json.dump(findings_data, f)
            
        registry_data = {
            "policy_rules": [
                {
                    "policy_rule_id": "PR001",
                    "priority": 100,
                    "trigger_finding_type": ["EVIDENCE_HIGH_SUPPORT"],
                    "policy_type": "POLICY_ACCEPT"
                },
                {
                    "policy_rule_id": "PR002",
                    "priority": 200,
                    "trigger_finding_type": ["CONFLICT_PRESENT", "EVIDENCE_INSUFFICIENT"],
                    "policy_type": "POLICY_REQUIRE_MORE_EVIDENCE"
                }
            ]
        }
        with open(self.mock_registry, "w", encoding="utf-8") as f:
            json.dump(registry_data, f)

    def tearDown(self):
        shutil.rmtree(self.output_dir, ignore_errors=True)
        for f in [self.mock_findings, self.mock_registry, "bad_policy_json.json"]:
            if os.path.exists(f): os.remove(f)

    def test_policy_generation(self):
        result = build_decision_policy(self.mock_findings, self.mock_registry, self.output_dir)
        
        self.assertEqual(result["reasoning_session_id"], "RSN-TEST")
        # Should aggregate by LRN-1 and LRN-2 => 2 policies
        self.assertEqual(len(result["policies"]), 2)
        
        # LRN-1 has FND-1 (HIGH_SUPPORT -> PR001/Prio100) and FND-2 (CONFLICT -> PR002/Prio200)
        # Winner for LRN-1 should be PR002
        p1 = next(p for p in result["policies"] if "LRN-1" in p["traceability"]["matched_learning_record_ids"])
        self.assertEqual(p1["policy_type"], "POLICY_REQUIRE_MORE_EVIDENCE")
        self.assertEqual(p1["applied_policy_rule_id"], "PR002")
        
        # LRN-2 has FND-3 which matches no rules
        p2 = next(p for p in result["policies"] if "LRN-2" in p["traceability"]["matched_learning_record_ids"])
        self.assertEqual(p2["policy_type"], POLICY_TYPE_NO_APPLICABLE_POLICY)
        self.assertEqual(p2["applied_policy_rule_id"], "NONE")
        
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, "decision_policy_registry.json")))

    def test_corrupted_artifacts(self):
        with open("bad_policy_json.json", "w") as f:
            f.write("{ bad json }")
        with self.assertRaises(PolicyError) as context:
            build_decision_policy("bad_policy_json.json", self.mock_registry, self.output_dir)
        self.assertIn("ARTIFACT_CORRUPTED", str(context.exception))

if __name__ == "__main__":
    unittest.main()
