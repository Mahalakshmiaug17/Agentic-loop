import json
import logging
import time
from typing import Any

class AgentLogger:
    def __init__(self, log_file: str = "agent_execution.log"):
        self.logger = logging.getLogger("AgentLoop")
        self.logger.setLevel(logging.INFO)
        handler = logging.FileHandler(log_file)
        handler.setFormatter(logging.Formatter("%(message)s"))
        if not self.logger.handlers:
            self.logger.addHandler(handler)

    def log_step(
        self,
        iteration: int,
        step_name: str,
        input_summary: Any,
        output_summary: Any,
        latency_ms: float,
        error: str = None
    ):
        entry = {
            "timestamp": time.time(),
            "iteration": iteration,
            "step": step_name,
            "input_summary": input_summary,
            "output_summary": output_summary,
            "latency_ms": round(latency_ms, 2),
            "error": error
        }
        self.logger.info(json.dumps(entry))
        print(f"[{step_name.upper()}] Iteration {iteration} | Latency: {entry['latency_ms']}ms | Status: {'ERROR' if error else 'OK'}")