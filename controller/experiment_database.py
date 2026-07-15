import json
import os

EXPERIMENT_DB_FILE = "experiment_database_index.json"

class ExperimentDatabase:
    def __init__(self, db_path=EXPERIMENT_DB_FILE):
        self.db_path = db_path
        self._initialize_db()
        
    def _initialize_db(self):
        if not os.path.exists(self.db_path):
            with open(self.db_path, "w", encoding="utf-8") as f:
                json.dump({"experiments": {}}, f, indent=4)
                
    def log_experiment(self, experiment_id, version, run_details):
        """
        Maintains history. Never overwrites. Supports versioning.
        run_details is a dict containing arbitrary experiment data.
        """
        with open(self.db_path, "r", encoding="utf-8") as f:
            db = json.load(f)
            
        if experiment_id not in db["experiments"]:
            db["experiments"][experiment_id] = {"versions": {}}
            
        # Ensure we never overwrite an existing version directly
        if version in db["experiments"][experiment_id]["versions"]:
            # If version exists, we append a timestamp to the version string to prevent overwrite
            import time
            version = f"{version}_{int(time.time())}"
            
        db["experiments"][experiment_id]["versions"][version] = run_details
        
        with open(self.db_path, "w", encoding="utf-8") as f:
            json.dump(db, f, indent=4)
            
        return version
