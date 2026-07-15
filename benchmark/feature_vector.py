import numpy as np
from feature_registry import FEATURE_REGISTRY, FEATURE_DIMENSION

def build_feature_vector(scalars_dict):
    """
    Builds a strictly ordered numpy.ndarray of fixed dimension N 
    based on the FEATURE_REGISTRY.
    """
    vector = np.zeros(FEATURE_DIMENSION, dtype=np.float32)
    
    for i, feature_name in enumerate(FEATURE_REGISTRY):
        vector[i] = scalars_dict.get(feature_name, 0.0)
        
    return vector
