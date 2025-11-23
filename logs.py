# app/logs.py
import datetime
import threading
from typing import List, Dict

class AgentLog:
    def __init__(self):
        self._lock = threading.Lock()
        self.entries: List[Dict] = []

    def add(self, agent_name: str, message: str, level="INFO", meta=None):
        with self._lock:
            self.entries.append({
                "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                "agent": agent_name,
                "level": level,
                "message": message,
                "meta": meta or {}
            })

    def all(self):
        with self._lock:
            return list(self.entries)

GLOBAL_LOG = AgentLog()
