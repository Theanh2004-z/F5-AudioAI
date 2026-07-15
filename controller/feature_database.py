import json
import os
from datetime import datetime

DATABASE_FILE = "feature_database_index.json"

class FeatureDatabase:
    def __init__(self, db_path=DATABASE_FILE):
        self.db_path = db_path
        self._initialize_db()
        
    def _initialize_db(self):
        if not os.path.exists(self.db_path):
            with open(self.db_path, "w", encoding="utf-8") as f:
                json.dump({"records": []}, f, indent=4)
                
    def add_record(self, experiment_id, timestamp, feature_vector_path, report_path, dashboard_path):
        with open(self.db_path, "r", encoding="utf-8") as f:
            db = json.load(f)
            
        record = {
            "experiment_id": experiment_id,
            "timestamp": timestamp,
            "feature_vector_path": feature_vector_path,
            "report_path": report_path,
            "dashboard_path": dashboard_path
        }
        
        db["records"].append(record)
        
        with open(self.db_path, "w", encoding="utf-8") as f:
            json.dump(db, f, indent=4)
            
        return record
