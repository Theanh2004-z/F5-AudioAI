"""
schema_validator.py
Checks schemas according to RULE-002.
"""
def check_schema_version(sample, expected_version):
    """
    Triggers RULE-002
    """
    if sample.get("dataset_schema_version") != "1.0.0":
        return False, ["RULE-002"]
    return True, []
