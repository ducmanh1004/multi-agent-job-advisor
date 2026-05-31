from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from pydantic import BaseModel, Field


class AgentTraceStep(BaseModel):
    name: str
    status: str = "succeeded"
    latency_ms: int = 0
    token_usage: int = 0
    message: str | None = None
    error: str | None = None
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    finished_at: datetime | None = None


class AgentTrace(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    workflow: str
    entity_id: str | None = None
    status: str = "succeeded"
    steps: list[AgentTraceStep] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

