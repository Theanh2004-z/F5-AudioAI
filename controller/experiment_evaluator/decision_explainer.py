"""
decision_explainer.py
Generates decision_explanation.json using a fixed deterministic template.
No AI, no NLP, just formatted string rules.
"""

DECISION_EXPLAINER_VERSION = "1.0.0"

def generate_decision_explanation(decision, profile, analysis_data):
    """
    Generates a deterministic explanation for the final decision.
    
    Args:
        decision: The final decision (PASS, PARTIAL_PASS, FAIL, INVALID).
        profile: The evaluation profile.
        analysis_data: Data loaded from analysis.json.
        
    Returns:
        dict: The explanation dictionary.
    """
    anomalies = analysis_data.get("anomalies_detected", {})
    
    corrupted = 1 if anomalies.get("corrupted_benchmark") else 0
    anomaly_count = 0
    if anomalies.get("has_nan"): anomaly_count += 1
    if anomalies.get("has_inf"): anomaly_count += 1
    if anomalies.get("missing_features"): anomaly_count += 1
    
    lines = [
        f"{decision} because:",
        f"- {profile['improved']} improved features",
        f"- {profile['degraded']} degraded features",
        f"- {profile['unchanged']} unchanged features",
        f"- {anomaly_count} anomalies detected",
        f"- {corrupted} corrupted benchmarks"
    ]
    
    explanation_text = "\n".join(lines)
    
    return {
        "decision": decision,
        "explanation": explanation_text,
        "details": {
            "improved": profile["improved"],
            "degraded": profile["degraded"],
            "unchanged": profile["unchanged"],
            "anomalies": anomaly_count,
            "corrupted": corrupted
        }
    }
