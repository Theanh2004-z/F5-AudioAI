"""
smoke_test.py
"""
import os
import sys
import json
import shutil
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from offline_learning_engine import train_offline_models
from learning_schema import OfflineLearningError

class TestOfflineLearningEngine(unittest.TestCase):
    def setUp(self):
        self.output_dir = "test_offline_learning"
        self.ds_path = "test_ds.json"
        self.rsn_path = "test_rsn.json"
        self.pol_path = "test_pol.json"
        
        ds = []
        for i in range(20):
            ds.append({
                "learning_record_id": f"LRN-{i}",
                "metadata": {"val": i},
                "feature_statistics": {"f1": {"mean": i*0.1}}
            })
        with open(self.ds_path, "w", encoding="utf-8") as f: json.dump(ds, f)
        
        with open(self.rsn_path, "w", encoding="utf-8") as f: json.dump({"findings": []}, f)
        
        pols = []
        for i in range(20):
            pols.append({
                "traceability": {"matched_learning_record_ids": [f"LRN-{i}"]},
                "policy_type": "POLICY_ACCEPT" if i % 2 == 0 else "POLICY_REJECT"
            })
        with open(self.pol_path, "w", encoding="utf-8") as f: json.dump({"policies": pols}, f)

    def tearDown(self):
        shutil.rmtree(self.output_dir, ignore_errors=True)
        for f in [self.ds_path, self.rsn_path, self.pol_path]:
            if os.path.exists(f): os.remove(f)

    def test_pipeline(self):
        res = train_offline_models(self.ds_path, self.rsn_path, self.pol_path, self.output_dir)
        self.assertIn("best_model", res)
        
        trained_dir = os.path.join(self.output_dir, "trained_models")
        self.assertTrue(os.path.exists(os.path.join(trained_dir, "production_model.pkl")))
        self.assertTrue(os.path.exists(os.path.join(trained_dir, "rf.pkl"))) # At least RF should be there
        
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, "model_registry.json")))

if __name__ == "__main__":
    unittest.main()
