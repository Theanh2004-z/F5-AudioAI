import json
import os
from benchmark_config import FEATURE_VECTOR_VERSION

def export_controller_input(feature_vector_path, differences, metadata, output_dir):
    """
    Its only responsibility is:
    feature_vector.npy -> controller_input.json
    No AI. No decision. No optimization.
    """
    controller_data = {
        "feature_vector_version": FEATURE_VECTOR_VERSION,
        "feature_vector_path": os.path.basename(feature_vector_path),
        "difference": differences,
        "metadata": metadata
    }
    
    out_path = os.path.join(output_dir, "controller_input.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(controller_data, f, indent=4)
        
    return out_path
