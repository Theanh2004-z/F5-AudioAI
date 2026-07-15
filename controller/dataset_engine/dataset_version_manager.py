"""
dataset_version_manager.py
Determines the next deterministic version based on registry state and schema changes.
"""

def get_next_version(registry, current_schema_version):
    """
    Returns the next Major.Minor.Patch version string.
    Major: Schema break.
    Minor: New build on identical schema.
    Patch: Metadata correction (not generated automatically by builder).
    """
    latest = registry.get_latest_dataset()
    if not latest:
        return "1.0.0"
        
    latest_v = latest.get("dataset_version", "1.0.0")
    parts = latest_v.split(".")
    try:
        major, minor, patch = map(int, parts)
    except ValueError:
        major, minor, patch = 1, 0, 0
        
    curr_major = int(current_schema_version.split(".")[0])
    
    if curr_major > major:
        return f"{curr_major}.0.0"
    else:
        return f"{major}.{minor + 1}.0"
