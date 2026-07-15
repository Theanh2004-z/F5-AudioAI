"""
intelligence_logger.py
"""
import time

class IntelligenceLogger:
    def __init__(self):
        self.start = time.time()
    def duration(self):
        return round(time.time() - self.start, 2)
