"""
inference_engine.py
"""
import os
import sys
import uuid
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from model_loader import load_production_artifacts
from feature_encoder import encode_features
from prediction_runner import execute_prediction
from prediction_explainer import explain_prediction
from inference_manifest import generate_manifest
from inference_registry import InferenceRegistry
from inference_logger import InferenceLogger

def run_inference(live_sample_path: str, model_registry_path: str, output_dir: str = "dataset/inference") -> dict:
    logger = InferenceLogger()
    os.makedirs(output_dir, exist_ok=True)
    registry = InferenceRegistry(output_dir)
    
    session_id = f"INF-{uuid.uuid4().hex[:8].upper()}"
    
    # 1. Load active model and pipeline
    model, pipeline = load_production_artifacts(model_registry_path)
    
    with open(live_sample_path, "r", encoding="utf-8") as f:
        live_sample = json.load(f)
        
    # 2. Encode
    X_encoded, feature_names = encode_features(live_sample, pipeline)
    
    # 3. Predict & Confidence
    pred_val, conf = execute_prediction(model, X_encoded)
    
    # 4. Explain
    explanation = explain_prediction(model, X_encoded, feature_names)
    
    # 5. Output
    output = {
        "inference_session_id": session_id,
        "prediction": {
            "prediction_value": pred_val,
            "confidence_score": conf,
            "explanation": explanation
        },
        "traceability": {
            "inference_timestamp": logger.get_timestamp()
        }
    }
    
    pred_path = os.path.join(output_dir, f"prediction_{session_id}.json")
    with open(pred_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=4)
        
    manifest, manifest_path = generate_manifest(session_id, live_sample_path, pred_path, output_dir)
    registry.register(session_id, pred_path, manifest_path)
    
    return output
