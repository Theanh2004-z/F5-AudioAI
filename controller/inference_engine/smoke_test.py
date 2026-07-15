"""
smoke_test.py
"""
import os
import sys
import json
import shutil
import unittest
import pickle

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from inference_engine import run_inference
from inference_schema import InferenceError

class MockModel:
    def predict(self, X): return [1]
    def predict_proba(self, X): return [[0.1, 0.9]]
    
class MockPipeline:
    def transform(self, X): return X.values

class TestInferenceEngine(unittest.TestCase):
    def setUp(self):
        self.output_dir = "test_inference_output"
        self.mock_models_dir = "trained_models"
        self.mock_registry = "test_model_registry.json"
        self.live_sample = "test_live_sample.json"
        
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.mock_models_dir, exist_ok=True)
        
        with open(os.path.join(self.mock_models_dir, "production_model.pkl"), "wb") as f:
            pickle.dump(MockModel(), f)
        with open(os.path.join(self.mock_models_dir, "feature_pipeline.pkl"), "wb") as f:
            pickle.dump(MockPipeline(), f)
            
        with open(self.mock_registry, "w") as f:
            json.dump({"records": [{"manifest_path": "fake"}]}, f)
            
        with open(self.live_sample, "w") as f:
            json.dump({
                "metadata": {"val": 1},
                "feature_statistics": {"f1": {"mean": 0.5}}
            }, f)

    def tearDown(self):
        shutil.rmtree(self.output_dir, ignore_errors=True)
        shutil.rmtree(self.mock_models_dir, ignore_errors=True)
        for f in [self.mock_registry, self.live_sample]:
            if os.path.exists(f): os.remove(f)

    def test_pipeline(self):
        res = run_inference(self.live_sample, self.mock_registry, self.output_dir)
        self.assertIn("prediction", res)
        self.assertEqual(res["prediction"]["prediction_value"], 1)
        self.assertEqual(res["prediction"]["confidence_score"], 0.9)
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, "inference_registry.json")))

if __name__ == "__main__":
    unittest.main()
