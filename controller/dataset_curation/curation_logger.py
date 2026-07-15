"""
curation_logger.py
Tracks execution duration.
"""
import time

class CurationLogger:
    def __init__(self):
        self.start = time.time()
    def duration(self):
        return round(time.time() - self.start, 2)
