"""
smoke_test.py
"""
import os
import sys
import json
import shutil
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from recommendation_engine import generate_recommendation
from recommendation_schema import ACTION_MANUAL_REVIEW

class TestRecommendationEngine(unittest.TestCase):
    def setUp(self):
        self.output_dir = "test_rec_output"
        self.pred_path = "test_prediction.json"
        self.rules_path = "test_rules.json"
        
        os.makedirs(self.output_dir, exist_ok=True)
        
        with open(self.pred_path, "w", encoding="utf-8") as f:
            json.dump({
                "inference_session_id": "INF-123",
                "prediction": {
                    "prediction_value": "REJECT",
                    "confidence_score": 0.95,
                    "explanation": "Prediction driven primarily by: feature_A (0.45)"
                }
            }, f)
            
        with open(self.rules_path, "w", encoding="utf-8") as f:
            json.dump({
                "rules": [
                    {
                        "condition": {
                            "prediction_value": "REJECT",
                            "min_confidence": 0.90,
                            "required_feature_in_explanation": "feature_A"
                        },
                        "action_id": "ACT-001",
                        "priority": 100,
                        "action_metadata": {"delta": -0.1}
                    },
                    {
                        "condition": {
                            "prediction_value": "REJECT"
                        },
                        "action_id": "ACT-002",
                        "priority": 50
                    }
                ]
            }, f)

    def tearDown(self):
        shutil.rmtree(self.output_dir, ignore_errors=True)
        for f in [self.pred_path, self.rules_path]:
            if os.path.exists(f): os.remove(f)

    def test_pipeline(self):
        res = generate_recommendation(self.pred_path, self.rules_path, self.output_dir)
        self.assertEqual(res["primary_action_id"], "ACT-001")
        self.assertEqual(res["action_metadata"]["delta"], -0.1)
        self.assertIn("ACT-002", res["alternative_action_ids"])
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, "recommendation_registry.json")))

    def test_fallback(self):
        with open("empty_rules.json", "w") as f: json.dump({"rules": []}, f)
        res = generate_recommendation(self.pred_path, "empty_rules.json", self.output_dir)
        self.assertEqual(res["primary_action_id"], ACTION_MANUAL_REVIEW)
        os.remove("empty_rules.json")

if __name__ == "__main__":
    unittest.main()
