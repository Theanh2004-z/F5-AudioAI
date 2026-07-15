"""
smoke_test.py
Smoke test for Stage 12 Revision 2 — Knowledge Graph & Relationship Engine.
Verifies pipeline execution, schema validation, index lookup, statistics computation,
and structural integrity of generated artifacts.
"""

import os
import sys
import json
import shutil
import unittest

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from knowledge_builder import run_knowledge_builder
from graph_validator import validate_graph_file
from knowledge_validator import validate_global_artifacts

class TestStage12Revision2(unittest.TestCase):
    def setUp(self):
        self.test_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "temp_smoke_test"))
        self.eval_base_dir = os.path.join(self.test_dir, "evaluation")
        self.knowledge_output_dir = os.path.join(self.test_dir, "knowledge")
        self.eval_registry_path = os.path.join(self.eval_base_dir, "evaluation_registry.json")

        os.makedirs(self.eval_base_dir, exist_ok=True)
        os.makedirs(self.knowledge_output_dir, exist_ok=True)

        # Create two qualifying mock evaluations (PASS / PARTIAL_PASS)
        # Evaluation 1: PASS
        self.eval_1_dir = os.path.join(self.eval_base_dir, "EVAL_001")
        os.makedirs(self.eval_1_dir, exist_ok=True)
        
        eval_manifest_1 = {
            "evaluation_id": "EVAL_001",
            "analysis_id": "ANALYSIS_001",
            "experiment_id": "EXP_001",
            "evaluator_version": "1.0.0",
            "timestamp": 123456789.0,
            "traceability": {
                "evaluation_id": "EVAL_001",
                "analysis_id": "ANALYSIS_001",
                "benchmark_id": "BENCH_001",
                "execution_id": "EXEC_001",
                "experiment_id": "EXP_001",
                "baseline_id": "BASE_V0",
                "lever": "pitch_lever",
                "planner_version": "1.0.0",
                "reasoning_version": "1.0.0",
                "executor_version": "1.0.0",
                "benchmark_version": "1.0.0",
                "analysis_version": "1.0.0",
                "evaluation_version": "1.0.0"
            }
        }
        with open(os.path.join(self.eval_1_dir, "evaluation_manifest.json"), "w", encoding="utf-8") as f:
            json.dump(eval_manifest_1, f, indent=4)

        scorecard_1 = {
            "feature_evaluations": [
                {"feature_index": 0, "outcome": "IMPROVED", "relative_delta_abs": 0.04},
                {"feature_index": 1, "outcome": "UNCHANGED", "relative_delta_abs": 0.01}
            ]
        }
        with open(os.path.join(self.eval_1_dir, "scorecard.json"), "w", encoding="utf-8") as f:
            json.dump(scorecard_1, f, indent=4)

        # Evaluation 2: PARTIAL_PASS
        self.eval_2_dir = os.path.join(self.eval_base_dir, "EVAL_002")
        os.makedirs(self.eval_2_dir, exist_ok=True)
        
        eval_manifest_2 = {
            "evaluation_id": "EVAL_002",
            "analysis_id": "ANALYSIS_002",
            "experiment_id": "EXP_002",
            "evaluator_version": "1.0.0",
            "timestamp": 123456790.0,
            "traceability": {
                "evaluation_id": "EVAL_002",
                "analysis_id": "ANALYSIS_002",
                "benchmark_id": "BENCH_002",
                "execution_id": "EXEC_002",
                "experiment_id": "EXP_002",
                "baseline_id": "BASE_V0",
                "lever": "pitch_lever",
                "planner_version": "1.0.0",
                "reasoning_version": "1.0.0",
                "executor_version": "1.0.0",
                "benchmark_version": "1.0.0",
                "analysis_version": "1.0.0",
                "evaluation_version": "1.0.0"
            }
        }
        with open(os.path.join(self.eval_2_dir, "evaluation_manifest.json"), "w", encoding="utf-8") as f:
            json.dump(eval_manifest_2, f, indent=4)

        scorecard_2 = {
            "feature_evaluations": [
                {"feature_index": 0, "outcome": "IMPROVED", "relative_delta_abs": 0.03},
                {"feature_index": 2, "outcome": "DEGRADED", "relative_delta_abs": 0.05}
            ]
        }
        with open(os.path.join(self.eval_2_dir, "scorecard.json"), "w", encoding="utf-8") as f:
            json.dump(scorecard_2, f, indent=4)

        # Evaluation Registry
        eval_registry = {
            "registry_version": "1.0.0",
            "total_registered": 2,
            "records": [
                {
                    "evaluation_id": "EVAL_001",
                    "analysis_id": "ANALYSIS_001",
                    "benchmark_id": "BENCH_001",
                    "execution_id": "EXEC_001",
                    "experiment_id": "EXP_001",
                    "evaluation_timestamp": 123456789.0,
                    "evaluation_directory": self.eval_1_dir,
                    "evaluation_status": "VALIDATED",
                    "evaluation_version": "1.0.0",
                    "decision": "PASS"
                },
                {
                    "evaluation_id": "EVAL_002",
                    "analysis_id": "ANALYSIS_002",
                    "benchmark_id": "BENCH_002",
                    "execution_id": "EXEC_002",
                    "experiment_id": "EXP_002",
                    "evaluation_timestamp": 123456790.0,
                    "evaluation_directory": self.eval_2_dir,
                    "evaluation_status": "VALIDATED",
                    "evaluation_version": "1.0.0",
                    "decision": "PARTIAL_PASS"
                }
            ]
        }
        with open(self.eval_registry_path, "w", encoding="utf-8") as f:
            json.dump(eval_registry, f, indent=4)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_pipeline_and_artifacts(self):
        # Run Knowledge Builder
        report = run_knowledge_builder(
            eval_registry_path=self.eval_registry_path,
            output_dir=self.knowledge_output_dir,
            eval_base_dir=self.eval_base_dir
        )

        # 1. Check report contents
        self.assertIn("graph_summary", report)
        self.assertIn("relationship_summary", report)
        self.assertIn("graph_statistics", report)

        # Verify graph sizes
        g_summary = report["graph_summary"]
        self.assertEqual(g_summary["total_nodes"], 10)

        # 2. Check global validator execution
        global_valid = validate_global_artifacts(self.knowledge_output_dir)
        self.assertTrue(global_valid)

        # 3. Check graph_validator details on generated graph file
        graph_path = os.path.join(self.knowledge_output_dir, "knowledge_graph.json")
        val_res = validate_graph_file(graph_path)
        self.assertTrue(val_res["is_valid"], f"Graph structural errors found: {val_res['errors']}")

        # 4. Check index lookup mapping correctness
        index_path = os.path.join(self.knowledge_output_dir, "knowledge_graph_index.json")
        with open(index_path, "r", encoding="utf-8") as f:
            idx_data = json.load(f)
        
        self.assertIn("pitch_lever", idx_data["levers"])
        lever_idx = idx_data["levers"]["pitch_lever"]
        self.assertIn("pitch_f0_mean", lever_idx["features"])
        self.assertIn("energy_rms_mean", lever_idx["features"])
        self.assertIn("speech_rate", lever_idx["features"])
        self.assertIn("EXP_001", lever_idx["experiments"])
        self.assertIn("EXP_002", lever_idx["experiments"])
        self.assertIn("EVAL_001", lever_idx["evaluations"])
        self.assertIn("EVAL_002", lever_idx["evaluations"])

        # 5. Check statistics computation correctness
        stats_path = os.path.join(self.knowledge_output_dir, "knowledge_graph_statistics.json")
        with open(stats_path, "r", encoding="utf-8") as f:
            stats_data = json.load(f)
        
        self.assertEqual(stats_data["total_nodes"], 10)
        self.assertEqual(stats_data["node_histogram"]["LEVER"], 1)
        self.assertEqual(stats_data["node_histogram"]["FEATURE"], 3)
        self.assertEqual(stats_data["node_histogram"]["EXPERIMENT"], 2)
        self.assertEqual(stats_data["node_histogram"]["EVALUATION"], 2)
        self.assertEqual(stats_data["node_histogram"]["KNOWLEDGE"], 2)
        
        # Edge Histogram checks
        self.assertEqual(stats_data["edge_histogram"]["LEVER_AFFECTS_FEATURE"], 3)
        self.assertEqual(stats_data["edge_histogram"]["LEVER_FROM_EXPERIMENT"], 2)
        self.assertEqual(stats_data["edge_histogram"]["EXPERIMENT_HAS_EVALUATION"], 2)
        self.assertEqual(stats_data["edge_histogram"]["EVALUATION_GENERATED_KNOWLEDGE"], 2)
        self.assertEqual(stats_data["edge_histogram"]["LEVER_SUPPORTED_BY"], 2)
        
        # LCC should be the entire connected graph (10 nodes)
        self.assertEqual(stats_data["largest_connected_component"], 10)

        # 6. Verify traceability fields in per-record manifest
        records_dir = report["build_records"][0]["knowledge_dir"]
        manifest_path = os.path.join(records_dir, "knowledge_manifest.json")
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
        
        self.assertIn("knowledge_graph_version", manifest)
        self.assertIn("relationship_engine_version", manifest)
        self.assertIn("graph_statistics_version", manifest)
        self.assertIn("graph_index_version", manifest)
        
        trace = manifest["traceability"]
        self.assertIn("knowledge_graph_version", trace)
        self.assertIn("relationship_engine_version", trace)
        self.assertIn("graph_statistics_version", trace)
        self.assertIn("graph_index_version", trace)

        print("\n[SmokeTest] ALL TESTS PASSED.")

if __name__ == "__main__":
    unittest.main()
