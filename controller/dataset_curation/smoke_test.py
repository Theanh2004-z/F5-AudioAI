"""
smoke_test.py
Verifies the Dataset Curation Engine functionality.
"""
import os
import sys
import json
import shutil
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from dataset_curation_engine import curate_dataset
from curation_registry import CurationRegistry

class TestDatasetCurationEngine(unittest.TestCase):
    def setUp(self):
        self.output_dir = "test_curated_output"
        self.mock_stage13_registry = "test_stage13_registry.json"
        self.mock_stage13_dataset = "test_stage13_dataset_v1.0.0.json"
        
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Valid Sample
        s1 = {"dataset_schema_version": "1.0.0", "sample_id": "S1", "experiment_id": "E1", "knowledge_id": "K1", "feature_deltas": {}, "decision": "PASS", "traceability": {"a": 1}}
        # Invalid Schema (RULE-002)
        s2 = {"dataset_schema_version": "0.9.0", "sample_id": "S2", "experiment_id": "E2", "knowledge_id": "K2", "feature_deltas": {}, "decision": "FAIL", "traceability": {"a": 1}}
        # Duplicate ID (RULE-003)
        s3 = {"dataset_schema_version": "1.0.0", "sample_id": "S1", "experiment_id": "E3", "knowledge_id": "K3", "feature_deltas": {}, "decision": "PASS", "traceability": {"a": 1}}
        # Missing Traceability (RULE-001) -> INCOMPLETE
        s4 = {"dataset_schema_version": "1.0.0", "sample_id": "S4", "experiment_id": "E4", "feature_deltas": {}, "decision": "PASS"}
        # Null Deltas (RULE-004) -> CORRUPTED
        s5 = {"dataset_schema_version": "1.0.0", "sample_id": "S5", "experiment_id": "E5", "knowledge_id": "K5", "feature_deltas": None, "decision": "PASS", "traceability": {"a": 1}}
        
        samples = [s1, s2, s3, s4, s5]
        with open(self.mock_stage13_dataset, "w", encoding="utf-8") as f:
            json.dump(samples, f)
            
        stage13_registry = {
            "records": [{
                "dataset_id": "DS-MOCK",
                "dataset_version": "1.0.0",
                "dataset_path": self.mock_stage13_dataset
            }]
        }
        with open(self.mock_stage13_registry, "w", encoding="utf-8") as f:
            json.dump(stage13_registry, f)
            
    def tearDown(self):
        shutil.rmtree(self.output_dir, ignore_errors=True)
        if os.path.exists(self.mock_stage13_registry):
            os.remove(self.mock_stage13_registry)
        if os.path.exists(self.mock_stage13_dataset):
            os.remove(self.mock_stage13_dataset)
            
    def test_curation(self):
        curate_dataset(self.mock_stage13_registry, self.output_dir)
        
        # Artifact existence
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, "curation_registry.json")))
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, "curated_dataset_v1.0.0.json")))
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, "quarantine_dataset.json")))
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, "curation_quality_report.json")))
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, "curated_manifest.json")))
        
        # Valid Dataset contains 1 sample
        with open(os.path.join(self.output_dir, "curated_dataset_v1.0.0.json"), "r") as f:
            valid_samples = json.load(f)
        self.assertEqual(len(valid_samples), 1)
        self.assertEqual(valid_samples[0]["sample_id"], "S1")
        
        # Quarantine contains 4 samples
        with open(os.path.join(self.output_dir, "quarantine_dataset.json"), "r") as f:
            quarantine = json.load(f)
        self.assertEqual(len(quarantine), 4)
        
        # Check reasons
        reasons = {}
        for q in quarantine:
            reasons[q["sample_id"]] = q["reason_codes"]
            
        self.assertIn("RULE-002", reasons["S2"])
        self.assertIn("RULE-003", reasons["S1"]) # S3 had sample_id S1
        self.assertIn("RULE-001", reasons["S4"])
        self.assertIn("RULE-004", reasons["S5"])

if __name__ == "__main__":
    unittest.main()
