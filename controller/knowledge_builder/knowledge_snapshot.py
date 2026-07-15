"""
knowledge_snapshot.py
Generates an immutable, append-only snapshot of the knowledge base state.
Snapshot includes SHA256 checksum of knowledge_base.json content.
"""

import json
import os
import hashlib
from datetime import datetime

KNOWLEDGE_SNAPSHOT_VERSION  = "1.0.0"
KNOWLEDGE_SNAPSHOT_FILENAME = "knowledge_snapshot.json"

def generate_snapshot(knowledge_base, knowledge_registry, global_stats, base_dir="knowledge"):
    """
    Creates an immutable snapshot record of the current knowledge base state.
    Appends to knowledge_snapshot.json (never overwrites old snapshots).
    
    Args:
        knowledge_base: KnowledgeBase instance.
        knowledge_registry: KnowledgeRegistry instance.
        global_stats: Output from knowledge_statistics.build_knowledge_statistics()
        base_dir: Output directory.
        
    Returns:
        dict: The new snapshot entry.
    """
    # Compute SHA256 checksum of the base file
    checksum = "NONE"
    base_path = knowledge_base.base_path
    if os.path.exists(base_path):
        with open(base_path, "rb") as f:
            checksum = hashlib.sha256(f.read()).hexdigest()

    snapshot_entry = {
        "snapshot_timestamp":        datetime.now().strftime("%Y%m%d_%H%M%S"),
        "knowledge_base_version":    knowledge_base.version,
        "registry_version":          knowledge_registry.version,
        "statistics_version":        global_stats.get("knowledge_statistics_version", "UNKNOWN"),
        "snapshot_version":          KNOWLEDGE_SNAPSHOT_VERSION,
        "total_levers":              global_stats.get("total_levers", 0),
        "total_records":             global_stats.get("total_records", 0),
        "knowledge_base_checksum":   checksum
    }

    # Append-only: load existing snapshots and append
    snapshot_path = os.path.join(base_dir, KNOWLEDGE_SNAPSHOT_FILENAME)
    existing = {"snapshots": []}
    if os.path.exists(snapshot_path):
        with open(snapshot_path, "r", encoding="utf-8") as f:
            existing = json.load(f)

    existing["snapshots"].append(snapshot_entry)
    existing["total_snapshots"] = len(existing["snapshots"])
    existing["latest_snapshot"] = snapshot_entry

    with open(snapshot_path, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=4)

    print(f"[KnowledgeSnapshot] Snapshot created. Checksum={checksum[:16]}...")
    return snapshot_entry
