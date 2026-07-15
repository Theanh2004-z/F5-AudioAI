"""
smoke_test.py
"""
import os
import sys
import json
import shutil
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from knowledge_retrieval_engine import retrieve_knowledge
from retrieval_schema import RetrievalError

class TestKnowledgeRetrievalEngine(unittest.TestCase):
    def setUp(self):
        self.output_dir = "test_retrieval_output"
        self.mock_registry = "test_learning_registry.json"
        self.mock_index = "learning_index.json"
        self.mock_dataset = "test_learning_dataset_v1.0.0.json"
        self.mock_query = "test_retrieval_query.json"
        
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Create dataset
        r1 = {"learning_record_id": "LRN-1", "metadata": {"lever": "L1", "parameter_name": "p1", "parameter_value": 1.0}}
        r2 = {"learning_record_id": "LRN-2", "metadata": {"lever": "L1", "parameter_name": "p2", "parameter_value": 2.0}}
        with open(self.mock_dataset, "w", encoding="utf-8") as f:
            json.dump([r1, r2], f)
            
        # Create index
        idx = {
            "L1": {
                "p1": {
                    "1.0": {"f1": {"learning_record_id": "LRN-1"}}
                },
                "p2": {
                    "2.0": {"f2": {"learning_record_id": "LRN-2"}}
                }
            }
        }
        with open(self.mock_index, "w", encoding="utf-8") as f:
            json.dump(idx, f)
            
        # Create registry
        reg = {
            "records": [{
                "dataset_version": "1.0.0",
                "dataset_path": self.mock_dataset
            }]
        }
        with open(self.mock_registry, "w", encoding="utf-8") as f:
            json.dump(reg, f)
            
        # Create valid query
        q = {
            "query_id": "QRY-TEST",
            "query_schema_version": "1.0.0",
            "requested_items": [
                {"lever": "L1", "parameter_name": "p1", "parameter_value": 1.0, "feature_name": "f1"},
                {"lever": "L1", "parameter_name": "p3", "parameter_value": 3.0, "feature_name": "f3"} # NOT_FOUND
            ]
        }
        with open(self.mock_query, "w", encoding="utf-8") as f:
            json.dump(q, f)

    def tearDown(self):
        shutil.rmtree(self.output_dir, ignore_errors=True)
        for f in [self.mock_registry, self.mock_index, self.mock_dataset, self.mock_query, "test_bad_query.json"]:
            if os.path.exists(f): os.remove(f)

    def test_retrieval(self):
        result = retrieve_knowledge(self.mock_query, self.mock_registry, self.output_dir)
        
        self.assertEqual(result["query_id"], "QRY-TEST")
        self.assertEqual(len(result["matched_records"]), 1)
        self.assertEqual(result["matched_records"][0]["learning_record_id"], "LRN-1")
        self.assertEqual(len(result["unmatched_requests"]), 1)
        self.assertEqual(result["unmatched_requests"][0]["parameter_name"], "p3")
        
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, "retrieval_registry.json")))
        
    def test_schema_mismatch(self):
        q = {"query_id": "Q", "query_schema_version": "0.1", "requested_items": []}
        with open("test_bad_query.json", "w", encoding="utf-8") as f:
            json.dump(q, f)
        with self.assertRaises(RetrievalError) as context:
            retrieve_knowledge("test_bad_query.json", self.mock_registry, self.output_dir)
        self.assertIn("SCHEMA_VERSION_MISMATCH", str(context.exception))
        
    def test_registry_missing(self):
        with self.assertRaises(RetrievalError):
            retrieve_knowledge(self.mock_query, "fake_registry.json", self.output_dir)

if __name__ == "__main__":
    unittest.main()
