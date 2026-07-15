"""
prediction_explainer.py
"""
def explain_prediction(model, X_encoded, feature_names):
    importance = {}
    if hasattr(model, "feature_importances_"):
        imps = model.feature_importances_
        for name, imp in zip(feature_names, imps):
            importance[name] = float(imp)
    else:
        for name in feature_names:
            importance[name] = 1.0 / len(feature_names)
            
    sorted_features = sorted(importance.items(), key=lambda x: x[1], reverse=True)[:3]
    explanation = f"Prediction driven primarily by: {', '.join([f'{k} ({v:.2f})' for k,v in sorted_features])}"
    return explanation
