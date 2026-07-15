"""
reasoning_logger.py
"""
import time

class ReasoningLogger:
    def __init__(self):
        self.start_time = time.time()
        
    def get_timestamp(self) -> float:
        return self.start_time
