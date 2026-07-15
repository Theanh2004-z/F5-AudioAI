"""
knowledge_retrieval_engine.py
"""
import os
import sys
import uuid
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from retrieval_schema import RETRIEVAL_SCHEMA_VERSION, RetrievalError
from query_parser import parse_query
from retrieval_loader import resolve_dataset_version
from index_router import route_query_item
from record_fetcher import fetch_records
from retrieval_manifest import generate_manifest
from retrieval_registry import RetrievalRegistry
from retrieval_logger import RetrievalLogger

def retrieve_knowledge(query_path: str, learning_registry_path: str, output_dir: str = "dataset/retrieval") -> dict:
    """Executes an exact-match query against the index and outputs a deterministic retrieval result."""
    logger = RetrievalLogger()
    os.makedirs(output_dir, exist_ok=True)
    registry = RetrievalRegistry(output_dir)
    
    session_id = f"RSESS-{uuid.uuid4().hex[:8].upper()}"
    
    query = parse_query(query_path)
    query_id = query.get("query_id")
    requested_version = query.get("requested_dataset_version")
    
    dataset_version, dataset_path, index_data = resolve_dataset_version(learning_registry_path, requested_version)
    
    requested_items = query.get("requested_items", [])
    matched_ids = set()
    item_routing = []
    
    for item in requested_items:
        r_id = route_query_item(index_data, item)
        item_routing.append((item, r_id))
        if r_id:
            matched_ids.add(r_id)
            
    fetched_records = fetch_records(dataset_path, matched_ids)
    
    matched_records = []
    unmatched_requests = []
    
    for r_id in sorted(list(matched_ids)):
        matched_records.append(fetched_records[r_id])
        
    for item, r_id in item_routing:
        if not r_id:
            unmatched_requests.append(item)
            
    result = {
        "retrieval_session_id": session_id,
        "query_id": query_id,
        "matched_records": matched_records,
        "unmatched_requests": unmatched_requests,
        "retrieval_manifest_version": RETRIEVAL_SCHEMA_VERSION,
        "learning_dataset_version": dataset_version,
        "traceability": {
            "retrieval_pipeline_timestamp": logger.get_timestamp()
        }
    }
    
    result_path = os.path.join(output_dir, f"retrieval_result_{session_id}.json")
    with open(result_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4)
        
    manifest, manifest_path = generate_manifest(session_id, query_path, result_path, output_dir, registry.version)
    
    registry.register(
        session_id=session_id,
        query_id=query_id,
        result_path=result_path,
        manifest_path=manifest_path,
        dataset_version=dataset_version,
        status="SUCCESS",
        checksum=manifest["result_checksum"]
    )
    
    return result
