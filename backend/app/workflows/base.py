from __future__ import annotations

import time
from collections.abc import Callable
from datetime import datetime, timezone
from typing import Any

from app.schemas.traces import AgentTrace, AgentTraceStep


class TraceRecorder:
    def __init__(self, workflow: str, entity_id: str | None = None) -> None:
        self.trace = AgentTrace(workflow=workflow, entity_id=entity_id)

    async def run(self, name: str, fn: Callable[[], Any]) -> Any:
        started = datetime.now(timezone.utc)
        start = time.perf_counter()
        step = AgentTraceStep(name=name, started_at=started)
        try:
            value = fn()
            if hasattr(value, "__await__"):
                value = await value
            step.status = "succeeded"
            return value
        except Exception as exc:
            step.status = "failed"
            step.error = str(exc)
            self.trace.status = "failed"
            raise
        finally:
            step.finished_at = datetime.now(timezone.utc)
            step.latency_ms = int((time.perf_counter() - start) * 1000)
            self.trace.steps.append(step)


