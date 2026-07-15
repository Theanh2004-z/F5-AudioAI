"""
prediction_parser.py
"""
import json
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from recommendation_schema import RecommendationError, ERROR_PREDICTION_CORRUPTED

def parse_prediction(prediction_path: str):
    if not os.path.exists(prediction_path):
        raise RecommendationError(ERROR_PREDICTION_CORRUPTED, f"Prediction file not found: {prediction_path}")
        
    try:
        with open(prediction_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        raise RecommendationError(ERROR_PREDICTION_CORRUPTED, f"Failed to parse prediction.json: {e}")
        
    pred = data.get("prediction", {})
    if "prediction_value" not in pred:
        raise RecommendationError(ERROR_PREDICTION_CORRUPTED, "Missing prediction_value.")
        
    return {
        "inference_session_id": data.get("inference_session_id"),
        "prediction_value": pred.get("prediction_value"),
        "confidence_score": pred.get("confidence_score"),
        "explanation": pred.get("explanation", "")
    }
