"""
knowledge_logger.py
Records runtime metadata for a knowledge build run.
"""

import time
import platform
import uuid
from knowledge_schema import KNOWLEDGE_BUILDER_VERSION

class KnowledgeLogger:
    def __init__(self, evaluation_id):
        self.evaluation_id      = evaluation_id
        self.knowledge_id       = f"KNOW-{uuid.uuid4().hex[:8]}"
        self.start_time         = None
        self.end_time           = None
        self.duration           = None
        self.status             = "PENDING"
        self.error_message      = None
        self.knowledge_version  = KNOWLEDGE_BUILDER_VERSION

    def start(self):
        self.start_time = time.time()
        self.status = "RUNNING"

    def stop(self, success=True, error=None):
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        self.status   = "COMPLETED" if success else "FAILED"
        if error:
            self.error_message = str(error)

    def get_runtime_record(self):
        return {
            "knowledge_id":      self.knowledge_id,
            "evaluation_id":     self.evaluation_id,
            "start_time":        self.start_time,
            "end_time":          self.end_time,
            "duration_sec":      round(self.duration, 4) if self.duration else 0.0,
            "status":            self.status,
            "error_message":     self.error_message,
            "knowledge_version": self.knowledge_version,
            "environment": {
                "platform":       platform.system(),
                "python_version": platform.python_version()
            }
        }
