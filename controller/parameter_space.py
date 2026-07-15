import json
import os
from parameter_registry import get_parameter_registry

PARAMETER_SPACE_FILE = "parameter_space.json"

def generate_parameter_space(output_path=PARAMETER_SPACE_FILE):
    """
    Creates a JSON representation of all tunable parameters.
    This file will become the only writable interface for future AI optimization.
    """
    registry = get_parameter_registry()
    
    # Initialize the space with default values
    space = {
        "metadata": {
            "version": 1,
            "description": "Writable interface for future AI Controller parameter tuning."
        },
        "parameters": {}
    }
    
    for param in registry:
        space["parameters"][param["name"]] = {
            "value": param["default_value"],
            "constraints": {
                "min": param["min"],
                "max": param["max"],
                "data_type": param["data_type"]
            }
        }
        
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(space, f, indent=4)
        
    return output_path

def read_parameter_space(input_path=PARAMETER_SPACE_FILE):
    if not os.path.exists(input_path):
        return None
    with open(input_path, "r", encoding="utf-8") as f:
        return json.load(f)
