"""
learning_logger.py
"""
import time
class LearningLogger:
    def __init__(self): self.start = time.time()
    def get_timestamp(self): return self.start
