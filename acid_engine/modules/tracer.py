# acid_engine/modules/tracer.py
import time
from typing import Dict, Any, List

class FunctionTrace:
    """Запись о выполнении одной функции."""
    def __init__(self, name: str):
        self.name = name
        self.start_time = None
        self.end_time = None
        self.status = "pending"  # success, failure
        self.error = None

    def start(self):
        self.start_time = time.time()

    def stop(self, error=None):
        self.end_time = time.time()
        self.status = "failure" if error else "success"
        self.error = str(error) if error else None

    @property
    def duration_ms(self):
        if self.start_time and self.end_time:
            return round((self.end_time - self.start_time) * 1000)
        return None


class Tracer:
    """Встроенный трассировщик выполнения модуля."""
    def __init__(self):
        self.traces: List[FunctionTrace] = []

    def trace(self, func_name: str):
        trace = FunctionTrace(func_name)
        self.traces.append(trace)
        return _TraceContext(trace)

    def report(self) -> str:
        lines = []
        lines.append("## Module Execution Report")
        for t in self.traces:
            status_icon = "✅" if t.status == "success" else "❌"
            duration = f"{t.duration_ms}ms" if t.duration_ms else "N/A"
            line = f"- {status_icon} **{t.name}** — {t.status.upper()} ({duration})"
            if t.error:
                line += f"\n  Error: {t.error}"
            lines.append(line)
        return "\n".join(lines)


class _TraceContext:
    def __init__(self, trace: FunctionTrace):
        self.trace = trace

    def __enter__(self):
        self.trace.start()
        return self.trace

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.trace.stop(error=exc_val)
        return False  # не подавляем исключения