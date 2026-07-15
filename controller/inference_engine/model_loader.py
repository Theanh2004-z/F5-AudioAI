"""
model_loader.py
"""
import os
import json
import pickle
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from inference_schema import InferenceError, ERROR_REGISTRY_RESOLUTION_FAILED, ERROR_ARTIFACT_MISSING

def load_production_artifacts(model_registry_path: str):
    if not os.path.exists(model_registry_path):
        raise InferenceError(ERROR_REGISTRY_RESOLUTION_FAILED, f"Registry not found: {model_registry_path}")
        
    try:
        with open(model_registry_path, "r", encoding="utf-8") as f:
            registry_data = json.load(f)
    except Exception:
        raise InferenceError(ERROR_REGISTRY_RESOLUTION_FAILED, "Failed to parse model_registry.json")
        
    records = registry_data.get("records", [])
    if not records:
        raise InferenceError(ERROR_REGISTRY_RESOLUTION_FAILED, "No trained models in registry.")
        
    registry_dir = os.path.dirname(model_registry_path)
    models_dir = os.path.join(registry_dir, "trained_models")
    
    prod_model_path = os.path.join(models_dir, "production_model.pkl")
    pipeline_path = os.path.join(models_dir, "feature_pipeline.pkl")
    
    if not os.path.exists(prod_model_path):
        raise InferenceError(ERROR_ARTIFACT_MISSING, f"Production model missing: {prod_model_path}")
    if not os.path.exists(pipeline_path):
        raise InferenceError(ERROR_ARTIFACT_MISSING, f"Feature pipeline missing: {pipeline_path}")
        
    try:
        with open(prod_model_path, "rb") as f:
            model = pickle.load(f)
        with open(pipeline_path, "rb") as f:
            pipeline = pickle.load(f)
    except Exception as e:
        raise InferenceError(ERROR_ARTIFACT_MISSING, f"Failed to load .pkl binaries: {e}")
        
    return model, pipeline
