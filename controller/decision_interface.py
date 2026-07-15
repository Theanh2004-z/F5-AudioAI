def create_decision_payload(feature_vector, feature_differences, parameter_registry):
    """
    Decision Interface.
    Receives:
    - feature vector
    - feature differences
    - parameter registry
    
    Returns ONLY a structured data object.
    NO optimization. NO AI inference. NO recommendation. Interface only.
    """
    
    decision_payload = {
        "state": {
            "feature_vector": feature_vector,
            "differences": feature_differences
        },
        "action_space": parameter_registry,
        "instructions": "This object is strictly an interface payload meant to be consumed by an external AI Controller."
    }
    
    return decision_payload
