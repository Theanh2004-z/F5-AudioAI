"""
benchmark_logger.py
Records runtime metadata (duration, platform, environment) for a benchmark run.
"""

import time
import platform
import uuid

class BenchmarkLogger:
    def __init__(self, execution_id, benchmark_version="1.0.0"):
        self.execution_id = execution_id
        self.benchmark_id = f"BENCH-{uuid.uuid4().hex[:8]}"
        self.start_time = None
        self.end_time = None
        self.duration = None
        self.status = "PENDING"
        self.error_message = None
        self.benchmark_version = benchmark_version
        
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
        """Returns the runtime metadata dict for benchmark_runtime.json"""
        return {
            "benchmark_id":      self.benchmark_id,
            "execution_id":      self.execution_id,
            "start_time":        self.start_time,
            "end_time":          self.end_time,
            "duration_sec":      round(self.duration, 4) if self.duration else 0.0,
            "status":            self.status,
            "error_message":     self.error_message,
            "benchmark_version": self.benchmark_version,
            "environment": {
                "platform":       platform.system(),
                "python_version": platform.python_version()
            }
        }
