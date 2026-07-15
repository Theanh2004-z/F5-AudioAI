"""
smoke_test.py
"""
import os
import sys
import json
import shutil
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from dataset_intelligence_engine import build_learning_dataset

class TestDatasetIntelligenceEngine(unittest.TestCase):
    def setUp(self):
        self.output_dir = "test_intelligence_output"
        self.mock_curation_registry = "test_curation_registry.json"
        self.mock_curated_dataset = "test_curated_dataset_v1.0.0.json"
        self.mock_curated_manifest = "test_curated_manifest.json"
        
        os.makedirs(self.output_dir, exist_ok=True)
        
        s1 = {"sample_id": "S1", "knowledge_id": "K1", "evaluation_id": "E1", "experiment_id": "X1", "lever": "L1", "parameter_values": {"p1": 1.0}, "decision": "PASS", "feature_deltas": {"f1": 0.05, "f2": 0.1}}
        s2 = {"sample_id": "S2", "knowledge_id": "K2", "evaluation_id": "E2", "experiment_id": "X2", "lever": "L1", "parameter_values": {"p1": 1.0}, "decision": "PASS", "feature_deltas": {"f1": 0.15, "f2": 0.2}}
        s3 = {"sample_id": "S3", "knowledge_id": "K3", "evaluation_id": "E3", "experiment_id": "X3", "lever": "L1", "parameter_values": {"p1": 2.0}, "decision": "FAIL", "feature_deltas": {"f1": 0.95}}
        
        with open(self.mock_curated_dataset, "w", encoding="utf-8") as f:
            json.dump([s1, s2, s3], f)
            
        with open(self.mock_curated_manifest, "w", encoding="utf-8") as f:
            json.dump({"curated_dataset_version": "1.0.0"}, f)
            
        registry = {
            "records": [{
                "dataset_path": self.mock_curated_dataset,
                "manifest_path": self.mock_curated_manifest
            }]
        }
        with open(self.mock_curation_registry, "w", encoding="utf-8") as f:
            json.dump(registry, f)
            
    def tearDown(self):
        shutil.rmtree(self.output_dir, ignore_errors=True)
        if os.path.exists(self.mock_curation_registry): os.remove(self.mock_curation_registry)
        if os.path.exists(self.mock_curated_dataset): os.remove(self.mock_curated_dataset)
        if os.path.exists(self.mock_curated_manifest): os.remove(self.mock_curated_manifest)
        
    def test_intelligence(self):
        build_learning_dataset(self.mock_curation_registry, self.output_dir)
        
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, "learning_registry.json")))
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, "learning_dataset_v1.0.0.json")))
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, "learning_index.json")))
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, "learning_statistics.json")))
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, "learning_manifest_v1.0.0.json")))
        
        with open(os.path.join(self.output_dir, "learning_dataset_v1.0.0.json"), "r") as f:
            records = json.load(f)
            
        self.assertEqual(len(records), 2)
        r1 = records[0]
        self.assertEqual(r1["metadata"]["parameter_value"], 1.0)
        self.assertIn("f1", r1["feature_statistics"])
        self.assertIn("f2", r1["feature_statistics"])
        self.assertEqual(r1["feature_statistics"]["f1"]["support_count"], 2)
        self.assertEqual(r1["feature_statistics"]["f1"]["evidence_strength"], "VERY_LOW")
        
        build_learning_dataset(self.mock_curation_registry, self.output_dir)
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, "learning_dataset_v1.1.0.json")))

if __name__ == "__main__":
    unittest.main()
