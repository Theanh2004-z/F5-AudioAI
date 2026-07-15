"""
smoke_test.py
Verifies the Dataset Engine functionality.
"""
import os
import sys
import json
import shutil
import unittest
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from dataset_engine import build_dataset
from dataset_registry import DatasetRegistry

class TestDatasetEngine(unittest.TestCase):
    def setUp(self):
        self.output_dir = "test_dataset_output"
        self.mock_registry_path = "test_mock_registry.json"
        self.mock_kb_dir = "test_mock_kb"
        
        # 1. Create a mock KB directory
        os.makedirs(self.mock_kb_dir, exist_ok=True)
        with open(os.path.join(self.mock_kb_dir, "knowledge_snapshot.json"), "w", encoding="utf-8") as f:
            json.dump({"knowledge_snapshot_version": "1.0.0"}, f)
            
        # 2. Create mock knowledge records
        os.makedirs(os.path.join(self.mock_kb_dir, "KNOW-001"), exist_ok=True)
        os.makedirs(os.path.join(self.mock_kb_dir, "KNOW-002"), exist_ok=True)
        
        # Semantic duplicate, different ID
        os.makedirs(os.path.join(self.mock_kb_dir, "KNOW-003"), exist_ok=True)
        
        for k_id in ["KNOW-001", "KNOW-002", "KNOW-003"]:
            k_dir = os.path.join(self.mock_kb_dir, k_id)
            with open(os.path.join(k_dir, "knowledge_profile.json"), "w", encoding="utf-8") as f:
                json.dump({"parameters": {"p1": 1}, "feature_deltas": {"f1": 0.5}}, f)
            with open(os.path.join(k_dir, "knowledge_evidence.json"), "w", encoding="utf-8") as f:
                json.dump({"observed_outcomes": {"f1": "IMPROVED"}}, f)
            with open(os.path.join(k_dir, "knowledge_manifest.json"), "w", encoding="utf-8") as f:
                json.dump({"timestamp": 1000.0, "traceability": {"execution_id": f"EXEC-{k_id}"}}, f)
                
        # 3. Create mock registry
        registry_data = {
            "records": [
                {"knowledge_id": "KNOW-001", "knowledge_directory": os.path.join(self.mock_kb_dir, "KNOW-001"), "knowledge_status": "VALIDATED", "experiment_id": "EXP-A", "evaluation_id": "EVAL-A", "decision": "PASS", "lever": "l1"},
                {"knowledge_id": "KNOW-002", "knowledge_directory": os.path.join(self.mock_kb_dir, "KNOW-002"), "knowledge_status": "VALIDATED", "experiment_id": "EXP-B", "evaluation_id": "EVAL-B", "decision": "FAIL", "lever": "l2"},
                # Technical duplicate retry (same exp, eval, knowledge)
                {"knowledge_id": "KNOW-002", "knowledge_directory": os.path.join(self.mock_kb_dir, "KNOW-002"), "knowledge_status": "VALIDATED", "experiment_id": "EXP-B", "evaluation_id": "EVAL-B", "decision": "FAIL", "lever": "l2"},
                # Semantic duplicate (different IDs, same params)
                {"knowledge_id": "KNOW-003", "knowledge_directory": os.path.join(self.mock_kb_dir, "KNOW-003"), "knowledge_status": "VALIDATED", "experiment_id": "EXP-C", "evaluation_id": "EVAL-C", "decision": "PASS", "lever": "l1"}
            ]
        }
        with open(self.mock_registry_path, "w", encoding="utf-8") as f:
            json.dump(registry_data, f)
            
    def tearDown(self):
        shutil.rmtree(self.output_dir, ignore_errors=True)
        shutil.rmtree(self.mock_kb_dir, ignore_errors=True)
        if os.path.exists(self.mock_registry_path):
            os.remove(self.mock_registry_path)
            
    def test_pipeline(self):
        # 1. Run build
        report = build_dataset(self.mock_registry_path, self.mock_kb_dir, self.output_dir)
        self.assertEqual(report["execution"]["status"], "COMPLETED")
        
        # 2. Check artifacts
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, "dataset_registry.json")))
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, "dataset_v1.0.0.json")))
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, "dataset_manifest_v1.0.0.json")))
        
        # 3. Check technical deduplication (4 records -> 3 samples)
        with open(os.path.join(self.output_dir, "dataset_v1.0.0.json"), "r", encoding="utf-8") as f:
            samples = json.load(f)
        self.assertEqual(len(samples), 3)
        
        # 4. Check deterministic sorting (EXP-A, EXP-B, EXP-C)
        self.assertEqual(samples[0]["experiment_id"], "EXP-A")
        self.assertEqual(samples[1]["experiment_id"], "EXP-B")
        self.assertEqual(samples[2]["experiment_id"], "EXP-C")
        
        # 5. Check semantic preservation (EXP-A and EXP-C have same parameters but both exist)
        self.assertEqual(samples[0]["parameter_values"], {"p1": 1})
        self.assertEqual(samples[2]["parameter_values"], {"p1": 1})
        
        # 6. Check unique SAMP- IDs
        samp_ids = set(s["sample_id"] for s in samples)
        self.assertEqual(len(samp_ids), 3)
        self.assertTrue(all(s.startswith("SAMP-") for s in samp_ids))
        
        # 7. Check Schema version presence
        self.assertTrue(all("dataset_schema_version" in s for s in samples))
        
        # 8. Check manifest 1:1 mapping
        with open(os.path.join(self.output_dir, "dataset_manifest_v1.0.0.json"), "r", encoding="utf-8") as f:
            manifest = json.load(f)
        self.assertEqual(manifest["dataset_path"], "dataset_v1.0.0.json")
        self.assertEqual(manifest["total_samples"], 3)
        self.assertNotEqual(manifest["checksum"], "pending")
        
        # 9. Test version increment
        build_dataset(self.mock_registry_path, self.mock_kb_dir, self.output_dir)
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, "dataset_v1.1.0.json")))
        
        registry = DatasetRegistry(self.output_dir)
        self.assertEqual(registry.data["total_datasets"], 2)

if __name__ == "__main__":
    unittest.main()
