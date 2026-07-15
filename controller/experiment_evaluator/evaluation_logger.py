"""
evaluation_logger.py
Records runtime metadata (duration, platform, environment) for an evaluation run.
"""

import time
import platform
import uuid

class EvaluationLogger:
    def __init__(self, analysis_id, evaluation_version="1.0.0"):
        self.analysis_id = analysis_id
        self.evaluation_id = f"EVAL-{uuid.uuid4().hex[:8]}"
        self.start_time = None
        self.end_time = None
        self.duration = None
        self.status = "PENDING"
        self.error_message = None
        self.evaluation_version = evaluation_version
        
    def start(self):
        self.start_time = time.time()
        self.status = "RUNNING"
        
    def stop(self, success=True, error=None):
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        self.status = "COMPLETED" if success else "FAILED"
        if error:
            self.error_message = str(error)
            
    def get_runtime_record(self):
        """Returns the runtime metadata dict for runtime.json"""
        return {
            "evaluation_id":       self.evaluation_id,
            "analysis_id":         self.analysis_id,
            "start_time":          self.start_time,
            "end_time":            self.end_time,
            "duration_sec":        round(self.duration, 4) if self.duration else 0.0,
            "status":              self.status,
            "error_message":       self.error_message,
            "evaluation_version":  self.evaluation_version,
            "environment": {
                "platform":       platform.system(),
                "python_version": platform.python_version()
            }
        }
