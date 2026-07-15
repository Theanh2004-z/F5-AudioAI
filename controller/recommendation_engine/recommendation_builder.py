"""
recommendation_builder.py
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from recommendation_schema import ACTION_MANUAL_REVIEW

def build_recommendation(primary_action, alternatives, parsed_prediction, session_id):
    if primary_action is None:
        primary_action_id = ACTION_MANUAL_REVIEW
        action_metadata = {"reason": "No applicable rules matched."}
    else:
        primary_action_id = primary_action["action_id"]
        action_metadata = primary_action.get("action_metadata", {})
        
    return {
        "recommendation_session_id": session_id,
        "inference_session_id": parsed_prediction.get("inference_session_id"),
        "primary_action_id": primary_action_id,
        "action_metadata": action_metadata,
        "alternative_action_ids": alternatives
    }
