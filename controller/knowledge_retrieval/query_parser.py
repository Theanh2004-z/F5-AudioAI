"""
query_parser.py
"""
import json
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from retrieval_schema import RetrievalError, ERROR_SCHEMA_VERSION_MISMATCH, RETRIEVAL_SCHEMA_VERSION

def parse_query(query_path: str) -> dict:
    """Parses and validates the immutable retrieval_query.json."""
    with open(query_path, "r", encoding="utf-8") as f:
        query = json.load(f)
        
    schema_version = query.get("query_schema_version", "")
    if schema_version != RETRIEVAL_SCHEMA_VERSION:
        raise RetrievalError(ERROR_SCHEMA_VERSION_MISMATCH, f"Expected {RETRIEVAL_SCHEMA_VERSION}, got {schema_version}")
        
    return query
