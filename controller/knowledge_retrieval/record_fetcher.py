"""
record_fetcher.py
"""
import json
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from retrieval_schema import RetrievalError, ERROR_RECORD_NOT_FOUND

def fetch_records(dataset_path: str, record_ids: set) -> dict:
    """Extracts exactly the records matched by their IDs. O(N) scan of dataset only once for extraction."""
    if not record_ids:
        return {}
        
    if not os.path.exists(dataset_path):
        raise RetrievalError(ERROR_RECORD_NOT_FOUND, f"Dataset file not found: {dataset_path}")
        
    with open(dataset_path, "r", encoding="utf-8") as f:
        dataset = json.load(f)
        
    fetched = {}
    for record in dataset:
        r_id = record.get("learning_record_id")
        if r_id in record_ids:
            fetched[r_id] = record
            
    for r_id in record_ids:
        if r_id not in fetched:
            raise RetrievalError(ERROR_RECORD_NOT_FOUND, f"learning_record_id {r_id} found in index but missing in dataset")
            
    return fetched
