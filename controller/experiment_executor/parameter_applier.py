"""
parameter_applier.py
Converts experiment parameters into the kwargs expected by the F5-TTS inference API.
No tuning. No validation beyond type checking.
"""

def extract_inference_kwargs(experiment, step_index=0):
    """
    Extracts the parameter value for a specific sweep step and formats
    it for the inference runner.
    
    Args:
        experiment: The planned experiment manifest dict.
        step_index: Which index of the parameter_range to apply.
        
    Returns:
        dict: kwargs to pass to F5 inference.
    """
    lever = experiment.get("parameter_name")
    param_range = experiment.get("parameter_range", [])
    
    if not lever or not param_range:
        raise ValueError(f"[ParameterApplier] Missing parameter_name or parameter_range in {experiment.get('experiment_id')}")
        
    if step_index >= len(param_range) or step_index < 0:
        raise IndexError(f"[ParameterApplier] step_index {step_index} out of bounds for range length {len(param_range)}")
        
    value = param_range[step_index]
    
    # Type check based on float/int inference, no tuning logic
    if isinstance(value, (int, float)):
        value = float(value)
        
    kwargs = {
        lever: value
    }
    
    return kwargs
