"""
offline_learning_engine.py
"""
import os
import sys
import uuid
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from dataset_builder import build_dataset
from feature_selector import process_features
from model_trainer import run_training_pipeline
from model_analyzer import analyze_model
from training_manifest import generate_manifest
from model_registry import ModelRegistry
from learning_logger import LearningLogger

def train_offline_models(learning_dataset_path: str, reasoning_findings_path: str, decision_policy_path: str, output_dir: str = "dataset/models") -> dict:
    logger = LearningLogger()
    os.makedirs(output_dir, exist_ok=True)
    models_dir = os.path.join(output_dir, "trained_models")
    registry = ModelRegistry(output_dir)
    
    session_id = f"ML-{uuid.uuid4().hex[:8].upper()}"
    
    # 1. Dataset Construction
    X_raw, y_raw = build_dataset(learning_dataset_path, reasoning_findings_path, decision_policy_path)
    
    # 2. Feature Selection
    X, feature_names, y = process_features(X_raw, y_raw)
    
    # 3 & 4. Train Models & Select Best
    best_model, stats = run_training_pipeline(X, y, models_dir)
    
    # Write stats
    stats_path = os.path.join(output_dir, f"training_statistics_{session_id}.json")
    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=4)
        
    # 5. Model Analysis
    importance = analyze_model(best_model, X, feature_names)
    imp_path = os.path.join(output_dir, f"feature_importance_{session_id}.json")
    with open(imp_path, "w", encoding="utf-8") as f:
        json.dump(importance, f, indent=4)
        
    # 6. Artifact Registration
    manifest, manifest_path = generate_manifest(session_id, learning_dataset_path, reasoning_findings_path, decision_policy_path, models_dir, output_dir)
    registry.register(session_id, stats["Winner"], stats, manifest_path)
    
    return {
        "learning_session_id": session_id,
        "best_model": stats["Winner"],
        "metrics": stats[stats["Winner"]],
        "traceability": {
            "pipeline_timestamp": logger.get_timestamp()
        }
    }
