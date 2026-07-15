"""
prediction_runner.py
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from inference_schema import InferenceError, ERROR_PREDICTION_FAILED

def execute_prediction(model, X_encoded):
    try:
        preds = model.predict(X_encoded)
        prediction_value = preds[0]
        
        confidence_score = None
        if hasattr(model, "predict_proba"):
            proba = model.predict_proba(X_encoded)
            confidence_score = float(max(proba[0]))
            
        return float(prediction_value) if isinstance(prediction_value, (int, float)) else prediction_value, confidence_score
    except Exception as e:
        raise InferenceError(ERROR_PREDICTION_FAILED, f"Model prediction crashed: {e}")
