"""
artifact_manager.py
Manages the execution directory and stores expected artifacts.
Do not overwrite previous executions.
"""

import os
import json


def setup_execution_directory(experiment_id, base_dir="executions"):
    """
    Creates a unique execution directory for the experiment run.
    Ensures it does not overwrite existing directories.
    
    Returns:
        str: Path to the new execution directory.
    """
    os.makedirs(base_dir, exist_ok=True)
    
    # Generate unique folder name based on experiment ID
    base_name = f"experiment_{experiment_id.replace('EXP-', '')}"
    target_dir = os.path.join(base_dir, base_name)
    
    # Avoid overwriting
    counter = 1
    while os.path.exists(target_dir):
        target_dir = os.path.join(base_dir, f"{base_name}_run{counter}")
        counter += 1
        
    os.makedirs(target_dir)
    return target_dir


def write_json_artifact(target_dir, filename, data):
    """Writes a JSON artifact to the execution directory."""
    path = os.path.join(target_dir, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def setup_log_files(target_dir):
    """
    Creates empty stdout.log and stderr.log files in the execution directory.
    Returns their paths.
    """
    stdout_path = os.path.join(target_dir, "stdout.log")
    stderr_path = os.path.join(target_dir, "stderr.log")
    
    with open(stdout_path, "w") as f:
        f.write("[ArtifactManager] stdout initialized.\n")
    with open(stderr_path, "w") as f:
        f.write("[ArtifactManager] stderr initialized.\n")
        
    return stdout_path, stderr_path
