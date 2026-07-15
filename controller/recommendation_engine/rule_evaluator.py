"""
rule_evaluator.py
"""
import json
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from recommendation_schema import RecommendationError, ERROR_RULES_MISSING

def evaluate_rules(parsed_prediction, rules_path):
    if not os.path.exists(rules_path):
        raise RecommendationError(ERROR_RULES_MISSING, f"Rules file not found: {rules_path}")
        
    with open(rules_path, "r", encoding="utf-8") as f:
        rules_data = json.load(f)
        
    matched_actions = []
    
    pred_val = parsed_prediction["prediction_value"]
    conf = parsed_prediction["confidence_score"]
    explanation = parsed_prediction["explanation"]
    
    for rule in rules_data.get("rules", []):
        condition = rule.get("condition", {})
        
        if "prediction_value" in condition:
            if str(pred_val) != str(condition["prediction_value"]):
                continue
                
        if "min_confidence" in condition and conf is not None:
            if conf < condition["min_confidence"]: continue
        if "max_confidence" in condition and conf is not None:
            if conf > condition["max_confidence"]: continue
            
        if "required_feature_in_explanation" in condition:
            req_feat = condition["required_feature_in_explanation"]
            if req_feat not in explanation:
                continue
                
        matched_actions.append({
            "action_id": rule.get("action_id"),
            "action_metadata": rule.get("action_metadata", {}),
            "priority": rule.get("priority", 0)
        })
        
    return matched_actions
