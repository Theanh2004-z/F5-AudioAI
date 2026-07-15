"""
model_analyzer.py
"""
def analyze_model(model, X, feature_names):
    importance = {}
    if hasattr(model, "feature_importances_"):
        imps = model.feature_importances_
        for name, imp in zip(feature_names, imps):
            importance[name] = float(imp)
    else:
        for name in feature_names:
            importance[name] = 1.0 / len(feature_names)
            
    return {"global_feature_importance": importance}
