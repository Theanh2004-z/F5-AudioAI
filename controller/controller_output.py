import json
import os

def export_schemas(output_dir="."):
    """
    Exports JSON schemas for controller input and output.
    These schemas must remain stable for future lightweight offline AI models.
    """
    input_schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "Controller Input Schema",
        "type": "object",
        "properties": {
            "state": {
                "type": "object",
                "properties": {
                    "feature_vector": {"type": "object"},
                    "differences": {"type": "object"}
                },
                "required": ["feature_vector", "differences"]
            },
            "action_space": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "min": {"type": "number"},
                        "max": {"type": "number"},
                        "data_type": {"type": "string"}
                    },
                    "required": ["name", "min", "max", "data_type"]
                }
            }
        },
        "required": ["state", "action_space"]
    }
    
    output_schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "Controller Output Schema",
        "type": "object",
        "properties": {
            "experiment_id": {"type": "string"},
            "timestamp": {"type": "string"},
            "recommended_parameters": {
                "type": "object",
                "additionalProperties": {"type": "number"}
            },
            "confidence_score": {"type": "number"}
        },
        "required": ["experiment_id", "timestamp", "recommended_parameters"]
    }
    
    os.makedirs(output_dir, exist_ok=True)
    
    in_schema_path = os.path.join(output_dir, "controller_input_schema.json")
    with open(in_schema_path, "w", encoding="utf-8") as f:
        json.dump(input_schema, f, indent=4)
        
    out_schema_path = os.path.join(output_dir, "controller_output_schema.json")
    with open(out_schema_path, "w", encoding="utf-8") as f:
        json.dump(output_schema, f, indent=4)
        
    return in_schema_path, out_schema_path

if __name__ == "__main__":
    export_schemas()
