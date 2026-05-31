from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_current_user
from app.db import repositories

router = APIRouter(prefix="/agent-traces", tags=["observability"])


@router.get("")
async def list_agent_traces(user: dict = Depends(get_current_user)) -> dict:
    return {"traces": repositories.list_traces()}


@router.get("/{trace_id}")
async def get_agent_trace(trace_id: str, user: dict = Depends(get_current_user)) -> dict:
    for trace in repositories.list_traces():
        if trace.id == trace_id:
            return {"trace": trace}
    raise HTTPException(status_code=404, detail="Trace not found")


