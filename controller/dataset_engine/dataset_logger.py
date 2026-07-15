"""
dataset_logger.py
Simple runtime tracking for the dataset engine.
"""
import time

class DatasetLogger:
    def __init__(self):
        self.start_time = time.time()
        self.end_time = None
        self.status = "RUNNING"
        self.error_message = None
        
    def stop(self, success=True, error=None):
        self.end_time = time.time()
        self.status = "COMPLETED" if success else "FAILED"
        if error:
            self.error_message = str(error)
            
    def get_runtime(self):
        if not self.end_time:
            self.end_time = time.time()
        return round(self.end_time - self.start_time, 2)
