"""
recommendation_engine.py
"""
import os
import sys
import uuid
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from prediction_parser import parse_prediction
from rule_evaluator import evaluate_rules
from action_ranker import rank_actions
from recommendation_builder import build_recommendation
from recommendation_manifest import generate_manifest
from recommendation_registry import RecommendationRegistry
from recommendation_logger import RecommendationLogger

def generate_recommendation(prediction_path: str, rules_path: str, output_dir: str = "dataset/recommendation") -> dict:
    logger = RecommendationLogger()
    os.makedirs(output_dir, exist_ok=True)
    registry = RecommendationRegistry(output_dir)
    
    session_id = f"REC-{uuid.uuid4().hex[:8].upper()}"
    
    parsed_pred = parse_prediction(prediction_path)
    matched_actions = evaluate_rules(parsed_pred, rules_path)
    primary_action, alternatives = rank_actions(matched_actions)
    
    rec_data = build_recommendation(primary_action, alternatives, parsed_pred, session_id)
    rec_data["traceability"] = {"recommendation_timestamp": logger.get_timestamp()}
    
    rec_path = os.path.join(output_dir, f"recommendation_{session_id}.json")
    with open(rec_path, "w", encoding="utf-8") as f:
        json.dump(rec_data, f, indent=4)
        
    manifest, manifest_path = generate_manifest(session_id, prediction_path, rec_path, output_dir)
    registry.register(session_id, rec_path, manifest_path)
    
    return rec_data
