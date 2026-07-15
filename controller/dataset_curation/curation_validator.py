"""
curation_validator.py
"""
def validate_curation(manifest, registry_entry):
    c1 = manifest["checksum"] == registry_entry["checksum"]
    c2 = manifest["curated_dataset_version"] == registry_entry["dataset_version"]
    c3 = manifest["total_samples"] == registry_entry["total_samples"]
    c4 = manifest["schema_version"] == "1.0.0"
    c5 = registry_entry is not None
    return c1 and c2 and c3 and c4 and c5
