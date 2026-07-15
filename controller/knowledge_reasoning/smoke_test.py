"""
smoke_test.py
"""
import os
import sys
import json
import shutil
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from reasoning_engine import execute_reasoning
from reasoning_schema import ReasoningError, FINDING_TYPE_NO_APPLICABLE_RULE

class TestKnowledgeReasoningEngine(unittest.TestCase):
    def setUp(self):
        self.output_dir = "test_reasoning_output"
        self.mock_retrieval = "test_retrieval_result.json"
        self.mock_rules = "test_reasoning_rule_registry.json"
        
        os.makedirs(self.output_dir, exist_ok=True)
        
        retrieval_data = {
            "retrieval_session_id": "RSESS-TEST",
            "matched_records": [
                {
                    "learning_record_id": "LRN-1",
                    "feature_statistics": {
                        "prosody": {"evidence_strength": "HIGH", "support_count": 25}
                    },
                    "traceability": {"source_sample_ids": ["S1"]}
                },
                {
                    "learning_record_id": "LRN-2",
                    "feature_statistics": {
                        "prosody": {"evidence_strength": "LOW", "support_count": 5}
                    },
                    "traceability": {"source_sample_ids": ["S2"]}
                }
            ]
        }
        with open(self.mock_retrieval, "w", encoding="utf-8") as f:
            json.dump(retrieval_data, f)
            
        rules_data = {
            "rules": [
                {
                    "rule_id": "R001",
                    "priority": 100,
                    "conditions": [
                        {"field": "feature_statistics.prosody.evidence_strength", "operator": "IN", "value": ["HIGH", "VERY_HIGH"]},
                        {"field": "feature_statistics.prosody.support_count", "operator": ">=", "value": 20}
                    ],
                    "finding_type": "EVIDENCE_HIGH_SUPPORT",
                    "explanation": "High support"
                },
                {
                    "rule_id": "R002",
                    "priority": 50,
                    "conditions": [
                        {"field": "feature_statistics.prosody.evidence_strength", "operator": "IN", "value": ["HIGH"]}
                    ],
                    "finding_type": "EVIDENCE_MODERATE",
                    "explanation": "Moderate"
                }
            ]
        }
        with open(self.mock_rules, "w", encoding="utf-8") as f:
            json.dump(rules_data, f)

    def tearDown(self):
        shutil.rmtree(self.output_dir, ignore_errors=True)
        for f in [self.mock_retrieval, self.mock_rules, "bad_json.json"]:
            if os.path.exists(f): os.remove(f)

    def test_reasoning(self):
        result = execute_reasoning(self.mock_retrieval, self.mock_rules, self.output_dir)
        
        self.assertEqual(result["retrieval_session_id"], "RSESS-TEST")
        self.assertEqual(len(result["findings"]), 2)
        
        # LRN-1 should match R001 (Priority 100 wins over 50)
        f1 = result["findings"][0]
        self.assertEqual(f1["rule_id"], "R001")
        self.assertEqual(f1["finding_type"], "EVIDENCE_HIGH_SUPPORT")
        
        # LRN-2 should match nothing
        f2 = result["findings"][1]
        self.assertEqual(f2["rule_id"], "NONE")
        self.assertEqual(f2["finding_type"], FINDING_TYPE_NO_APPLICABLE_RULE)
        
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, "reasoning_registry.json")))

    def test_corrupted_artifacts(self):
        with open("bad_json.json", "w") as f:
            f.write("{ bad json }")
        with self.assertRaises(ReasoningError) as context:
            execute_reasoning("bad_json.json", self.mock_rules, self.output_dir)
        self.assertIn("ARTIFACT_CORRUPTED", str(context.exception))

if __name__ == "__main__":
    unittest.main()
