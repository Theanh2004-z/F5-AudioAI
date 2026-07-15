"""
inference_logger.py
"""
import time
class InferenceLogger:
    def __init__(self): self.start = time.time()
    def get_timestamp(self): return self.start
