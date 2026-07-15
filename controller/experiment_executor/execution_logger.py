"""
execution_logger.py
Records execution runtime metadata (duration, platform, environment).
"""

import time
import platform
import uuid


class ExecutionLogger:
    def __init__(self, experiment_id):
        self.experiment_id = experiment_id
        self.execution_id = f"EXEC-{uuid.uuid4().hex[:8]}"
        self.start_time = None
        self.end_time = None
        self.duration = None
        self.status = "PENDING"
        self.error_message = None
        
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
            "execution_id":  self.execution_id,
            "experiment_id": self.experiment_id,
            "start_time":    self.start_time,
            "end_time":      self.end_time,
            "duration_sec":  round(self.duration, 4) if self.duration else 0.0,
            "status":        self.status,
            "error_message": self.error_message,
            "environment": {
                "platform":       platform.system(),
                "python_version": platform.python_version(),
                "f5_tts_version": "UNKNOWN" # To be resolved when integrated natively
            }
        }
