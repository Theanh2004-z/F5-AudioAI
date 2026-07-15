"""
knowledge_builder.py
Main Orchestrator for Stage 12 - Knowledge Builder (Rev 1: Global Knowledge Base).
10-phase pipeline. No AI, no ML, no optimization. Deterministic only.
"""

import os
import sys
import json
import time
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from knowledge_schema       import KNOWLEDGE_BUILDER_VERSION, QUALIFYING_DECISIONS
from evaluation_loader      import load_qualifying_evaluations
from knowledge_extractor    import extract_knowledge
from knowledge_aggregator   import aggregate_by_lever
from evidence_builder       import build_evidence
from knowledge_base         import KnowledgeBase, KNOWLEDGE_BASE_VERSION
from knowledge_index        import build_knowledge_index, KNOWLEDGE_INDEX_VERSION
from knowledge_statistics   import build_knowledge_statistics, KNOWLEDGE_STATISTICS_VERSION
from knowledge_consistency  import run_consistency_checks
from knowledge_snapshot     import generate_snapshot, KNOWLEDGE_SNAPSHOT_VERSION
from knowledge_registry     import KnowledgeRegistry
from knowledge_logger       import KnowledgeLogger
from knowledge_validator    import validate_knowledge, validate_global_artifacts
from relationship_builder   import RELATIONSHIP_ENGINE_VERSION
from knowledge_graph        import build_knowledge_graph, KNOWLEDGE_GRAPH_VERSION
from graph_index            import build_graph_index, GRAPH_INDEX_VERSION
from graph_statistics       import build_graph_statistics, GRAPH_STATISTICS_VERSION

REPORT_FILENAME = "knowledge_report.json"

def write_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def build_traceability(eval_record, eval_dir, knowledge_id,
                       knowledge_base_version, knowledge_statistics_version,
                       knowledge_snapshot_version, knowledge_index_version,
                       knowledge_graph_version, relationship_engine_version,
                       graph_statistics_version, graph_index_version):
    """Reads evaluation manifest and builds full 22-field traceability."""
    trace = {}
    manifest_path = os.path.join(eval_dir, "evaluation_manifest.json")
    if os.path.exists(manifest_path):
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
        trace = manifest.get("traceability", {})

    return {
        "knowledge_id":                knowledge_id,
        "evaluation_id":               eval_record.get("evaluation_id", "UNKNOWN"),
        "analysis_id":                 eval_record.get("analysis_id", trace.get("analysis_id", "UNKNOWN")),
        "benchmark_id":                eval_record.get("benchmark_id", trace.get("benchmark_id", "UNKNOWN")),
        "execution_id":                eval_record.get("execution_id", trace.get("execution_id", "UNKNOWN")),
        "experiment_id":               eval_record.get("experiment_id", trace.get("experiment_id", "UNKNOWN")),
        "baseline_id":                 trace.get("baseline_id", "UNKNOWN"),
        "planner_version":             trace.get("planner_version", "UNKNOWN"),
        "reasoning_version":           trace.get("reasoning_version", "UNKNOWN"),
        "executor_version":            trace.get("executor_version", "UNKNOWN"),
        "benchmark_version":           trace.get("benchmark_version", "UNKNOWN"),
        "analysis_version":            trace.get("analysis_version", "UNKNOWN"),
        "evaluation_version":          trace.get("evaluation_version", "UNKNOWN"),
        "knowledge_builder_version":   KNOWLEDGE_BUILDER_VERSION,
        "knowledge_base_version":      knowledge_base_version,
        "knowledge_statistics_version": knowledge_statistics_version,
        "knowledge_snapshot_version":  knowledge_snapshot_version,
        "knowledge_index_version":     knowledge_index_version,
        "knowledge_graph_version":     knowledge_graph_version,
        "relationship_engine_version": relationship_engine_version,
        "graph_statistics_version":    graph_statistics_version,
        "graph_index_version":          graph_index_version
    }

def build_knowledge_profile(knowledge_data, aggregation):
    features  = knowledge_data.get("observed_features", [])
    lever     = knowledge_data.get("lever", "UNKNOWN")
    agg_row   = aggregation.get(lever, {})
    outcome_counts = {"IMPROVED": 0, "UNCHANGED": 0, "DEGRADED": 0, "ERROR": 0}
    for f in features:
        o = f.get("outcome", "ERROR")
        outcome_counts[o] = outcome_counts.get(o, 0) + 1
    return {
        "lever":                      lever,
        "decision":                   knowledge_data.get("decision"),
        "total_features":             len(features),
        "improved_features":          outcome_counts["IMPROVED"],
        "unchanged_features":         outcome_counts["UNCHANGED"],
        "degraded_features":          outcome_counts["DEGRADED"],
        "error_features":             outcome_counts["ERROR"],
        "lever_total_observations":   agg_row.get("total_observations", 1),
        "lever_pass_count":           agg_row.get("pass_count", 0),
        "lever_partial_pass_count":   agg_row.get("partial_pass_count", 0)
    }

def build_record_statistics(knowledge_data, aggregation):
    lever    = knowledge_data.get("lever", "UNKNOWN")
    agg_row  = aggregation.get(lever, {})
    feature_histogram = {"IMPROVED": 0, "UNCHANGED": 0, "DEGRADED": 0, "ERROR": 0}
    for f in knowledge_data.get("observed_features", []):
        o = f.get("outcome", "ERROR")
        feature_histogram[o] = feature_histogram.get(o, 0) + 1
    return {
        "lever_histogram":    {lever: agg_row.get("total_observations", 1)},
        "decision_histogram": {
            "PASS":         agg_row.get("pass_count", 0),
            "PARTIAL_PASS": agg_row.get("partial_pass_count", 0),
            "FAIL":         agg_row.get("fail_count", 0)
        },
        "baseline_histogram": {knowledge_data.get("baseline_id", "UNKNOWN"): 1},
        "feature_histogram":  feature_histogram
    }

def run_knowledge_builder(eval_registry_path, output_dir="knowledge", eval_base_dir="evaluation"):
    """10-phase Knowledge Builder pipeline."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs(output_dir, exist_ok=True)

    registry = KnowledgeRegistry(registry_dir=output_dir)
    kb       = KnowledgeBase(base_dir=output_dir)

    # ── PHASE 1: Load Qualifying Evaluations ─────────────────────────────
    qualifying = load_qualifying_evaluations(eval_registry_path, registry.registry_path)

    summary = {
        "total_qualifying_loaded":   len(qualifying),
        "total_builds_attempted":    0,
        "total_completed":           0,
        "total_failed":              0,
        "total_validated":           0
    }
    knowledge_records_raw = []
    build_records         = []

    # ── PHASE 2: Extract (first pass) ────────────────────────────────────
    for eval_record in qualifying:
        eval_id  = eval_record.get("evaluation_id", "")
        eval_dir = eval_record.get("evaluation_directory", "")
        if not eval_dir:
            eval_dir = os.path.join(eval_base_dir, eval_id)
        try:
            kdata = extract_knowledge(eval_record, eval_dir)
            knowledge_records_raw.append((eval_record, eval_dir, kdata))
        except Exception as e:
            print(f"[KnowledgeBuilder] Extract error for {eval_id}: {e}")

    # ── PHASE 3: Aggregate across all records ─────────────────────────────
    raw_kdata_list = [kd for _, _, kd in knowledge_records_raw]
    aggregation    = aggregate_by_lever(raw_kdata_list)

    # ── PHASE 4: Evidence build (per lever) ───────────────────────────────
    lever_evidence = {}
    for lever, agg_row in aggregation.items():
        lever_evidence[lever] = build_evidence(lever, agg_row, raw_kdata_list)

    # ── PHASE 5: Knowledge Base upsert ───────────────────────────────────
    # Collect knowledge_ids per lever first (need logger IDs)
    lever_knowledge_ids = {l: [] for l in aggregation}

    # ── PHASES 6–7: Build per-record artifacts ────────────────────────────
    for eval_record, eval_dir, knowledge_data in knowledge_records_raw:
        eval_id = eval_record.get("evaluation_id", "")
        lever   = knowledge_data.get("lever", "UNKNOWN")

        summary["total_builds_attempted"] += 1
        logger   = KnowledgeLogger(eval_id)
        know_dir = os.path.join(output_dir, logger.knowledge_id)
        os.makedirs(know_dir, exist_ok=True)
        lever_knowledge_ids.setdefault(lever, []).append(logger.knowledge_id)

        print(f"\n[KnowledgeBuilder] Building {logger.knowledge_id} from {eval_id}")

        try:
            logger.start()
            agg_row  = aggregation.get(lever, {})
            evidence = lever_evidence.get(lever, {})

            traceability = build_traceability(
                eval_record, eval_dir, logger.knowledge_id,
                knowledge_base_version    = KNOWLEDGE_BASE_VERSION,
                knowledge_statistics_version = KNOWLEDGE_STATISTICS_VERSION,
                knowledge_snapshot_version= KNOWLEDGE_SNAPSHOT_VERSION,
                knowledge_index_version   = KNOWLEDGE_INDEX_VERSION,
                knowledge_graph_version   = KNOWLEDGE_GRAPH_VERSION,
                relationship_engine_version = RELATIONSHIP_ENGINE_VERSION,
                graph_statistics_version  = GRAPH_STATISTICS_VERSION,
                graph_index_version       = GRAPH_INDEX_VERSION
            )

            # knowledge.json
            knowledge_out = {
                "knowledge_id":      logger.knowledge_id,
                "evaluation_id":     eval_id,
                "experiment_id":     knowledge_data.get("experiment_id"),
                "lever":             lever,
                "observed_features": knowledge_data.get("observed_features", []),
                "decision":          knowledge_data.get("decision"),
                "baseline_id":       knowledge_data.get("baseline_id"),
                "timestamp":         logger.start_time
            }
            write_json(os.path.join(know_dir, "knowledge.json"), knowledge_out)
            write_json(os.path.join(know_dir, "knowledge_profile.json"),
                       build_knowledge_profile(knowledge_data, aggregation))
            write_json(os.path.join(know_dir, "knowledge_evidence.json"), evidence)
            write_json(os.path.join(know_dir, "knowledge_statistics.json"),
                       build_record_statistics(knowledge_data, aggregation))

            logger.stop(success=True)
            summary["total_completed"] += 1

        except Exception as e:
            logger.stop(success=False, error=e)
            summary["total_failed"] += 1
            traceability = {
                "knowledge_id": logger.knowledge_id,
                "knowledge_builder_version": KNOWLEDGE_BUILDER_VERSION,
                "knowledge_base_version": KNOWLEDGE_BASE_VERSION,
                "knowledge_statistics_version": KNOWLEDGE_STATISTICS_VERSION,
                "knowledge_snapshot_version": KNOWLEDGE_SNAPSHOT_VERSION,
                "knowledge_index_version": KNOWLEDGE_INDEX_VERSION,
                "knowledge_graph_version": KNOWLEDGE_GRAPH_VERSION,
                "relationship_engine_version": RELATIONSHIP_ENGINE_VERSION,
                "graph_statistics_version": GRAPH_STATISTICS_VERSION,
                "graph_index_version": GRAPH_INDEX_VERSION,
                **{f: "UNKNOWN" for f in [
                    "evaluation_id","analysis_id","benchmark_id","execution_id",
                    "experiment_id","baseline_id","planner_version","reasoning_version",
                    "executor_version","benchmark_version","analysis_version","evaluation_version"
                ]}
            }
            print(f"[KnowledgeBuilder] ERROR: {e}")

        runtime = logger.get_runtime_record()
        write_json(os.path.join(know_dir, "runtime.json"), runtime)

        manifest = {
            "knowledge_id":    logger.knowledge_id,
            "evaluation_id":   eval_id,
            "experiment_id":   knowledge_data.get("experiment_id", "UNKNOWN"),
            "timestamp":       logger.start_time if logger.start_time else time.time(),
            "builder_version": KNOWLEDGE_BUILDER_VERSION,
            "knowledge_graph_version": KNOWLEDGE_GRAPH_VERSION,
            "relationship_engine_version": RELATIONSHIP_ENGINE_VERSION,
            "graph_statistics_version": GRAPH_STATISTICS_VERSION,
            "graph_index_version": GRAPH_INDEX_VERSION,
            "traceability":    traceability
        }
        write_json(os.path.join(know_dir, "knowledge_manifest.json"), manifest)

        registry.register({
            "knowledge_id":        logger.knowledge_id,
            "evaluation_id":       eval_id,
            "experiment_id":       knowledge_data.get("experiment_id", "UNKNOWN"),
            "knowledge_directory": know_dir,
            "knowledge_status":    logger.status,
            "knowledge_version":   logger.knowledge_version,
            "decision":            knowledge_data.get("decision", "UNKNOWN"),
            "lever":               lever
        })

        is_valid = validate_knowledge(know_dir, logger.knowledge_id, registry)
        if is_valid:
            summary["total_validated"] += 1
            final_status = "VALIDATED"
        else:
            final_status = "INVALID" if logger.status == "COMPLETED" else "FAILED"

        build_records.append({
            "knowledge_id":  logger.knowledge_id,
            "evaluation_id": eval_id,
            "decision":      knowledge_data.get("decision"),
            "lever":         lever,
            "status":        final_status,
            "knowledge_dir": know_dir,
            "duration_sec":  runtime["duration_sec"],
            "error_message": logger.error_message
        })

    # ── PHASE 5 (deferred): Upsert knowledge base per lever ──────────────
    for lever, agg_row in aggregation.items():
        evidence = lever_evidence.get(lever, {})
        kids     = lever_knowledge_ids.get(lever, [])
        kb.upsert_lever(lever, agg_row, evidence, kids)

    # ── RELATIONSHIP ENGINE & GRAPH GENERATION ────────────────────────────
    graph = build_knowledge_graph(kb.get_all_levers(), registry, output_dir)
    graph_idx = build_graph_index(graph, output_dir)
    graph_stats = build_graph_statistics(graph, output_dir)

    # ── PHASE 8: Build Index ──────────────────────────────────────────────
    knowledge_index = build_knowledge_index(kb.get_all_levers(), output_dir)

    # ── PHASE 9: Global Statistics ────────────────────────────────────────
    global_stats = build_knowledge_statistics(kb.get_all_levers(), output_dir)

    # ── PHASE 10a: Consistency Check ─────────────────────────────────────
    consistency = run_consistency_checks(kb.get_all_levers(), registry, output_dir)

    # ── PHASE 10b: Snapshot ───────────────────────────────────────────────
    snapshot = generate_snapshot(kb, registry, global_stats, output_dir)

    # ── Validate global artifacts ─────────────────────────────────────────
    global_valid = validate_global_artifacts(output_dir)

    # ── Export Report ─────────────────────────────────────────────────────
    report = {
        "metadata": {
            "knowledge_builder_version": KNOWLEDGE_BUILDER_VERSION,
            "timestamp":                 timestamp,
            "eval_registry_file":        os.path.basename(eval_registry_path)
        },
        "knowledge_summary": summary,
        "knowledge_base_summary": {
            "total_levers":   global_stats.get("total_levers", 0),
            "total_records":  global_stats.get("total_records", 0),
            "total_support":  global_stats.get("total_support", 0),
            "pass_ratio":     global_stats.get("pass_ratio", 0.0),
            "partial_ratio":  global_stats.get("partial_ratio", 0.0)
        },
        "graph_summary": {
            "total_nodes": graph_stats.get("total_nodes", 0),
            "total_edges": graph_stats.get("total_edges", 0),
            "largest_connected_component": graph_stats.get("largest_connected_component", 0)
        },
        "relationship_summary": {
            "edge_histogram": graph_stats.get("edge_histogram", {})
        },
        "graph_statistics": graph_stats,
        "consistency_summary": {
            "overall_passed": consistency.get("overall_passed", False),
            "total_issues":   consistency.get("total_issues", 0)
        },
        "snapshot_summary": {
            "checksum": snapshot.get("knowledge_base_checksum", "NONE")[:16] + "...",
            "timestamp": snapshot.get("snapshot_timestamp")
        },
        "lever_aggregation": aggregation,
        "build_records":     build_records,
        "global_artifacts_valid": global_valid
    }
    write_json(os.path.join(output_dir, REPORT_FILENAME), report)

    print(f"\n[KnowledgeBuilder] Done. Report -> {os.path.join(output_dir, REPORT_FILENAME)}")
    return report

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--eval_registry",  required=True)
    parser.add_argument("--output_dir",     default="knowledge")
    parser.add_argument("--eval_base_dir",  default="evaluation")
    args = parser.parse_args()
    run_knowledge_builder(args.eval_registry, args.output_dir, args.eval_base_dir)
