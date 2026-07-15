"""
analysis_logger.py
Records runtime metadata (duration, platform, environment) for an analysis run.
"""

import time
import platform
import uuid

class AnalysisLogger:
    def __init__(self, benchmark_id, analysis_version="1.0.0"):
        self.benchmark_id = benchmark_id
        self.analysis_id = f"ANALYSIS-{uuid.uuid4().hex[:8]}"
        self.start_time = None
        self.end_time = None
        self.duration = None
        self.status = "PENDING"
        self.error_message = None
        self.analysis_version = analysis_version
        
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
            "analysis_id":       self.analysis_id,
            "benchmark_id":      self.benchmark_id,
            "start_time":        self.start_time,
            "end_time":          self.end_time,
            "duration_sec":      round(self.duration, 4) if self.duration else 0.0,
            "status":            self.status,
            "error_message":     self.error_message,
            "analysis_version":  self.analysis_version,
            "environment": {
                "platform":       platform.system(),
                "python_version": platform.python_version()
            }
        }
