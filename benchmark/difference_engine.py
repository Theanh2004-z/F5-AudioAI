from feature_registry import FEATURE_REGISTRY

def calculate_difference(ref_scalars, gen_scalars):
    """
    Calculates the raw numerical difference between reference and generated scalar features.
    NO evaluation, NO recommendation, NO overall score.
    """
    differences = {}
    
    for feature_name in FEATURE_REGISTRY:
        ref_val = ref_scalars.get(feature_name, 0.0)
        gen_val = gen_scalars.get(feature_name, 0.0)
        
        diff = gen_val - ref_val
        differences[f"{feature_name}_difference"] = diff
        
    return differences
