from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_current_user
from app.db import repositories
from app.workflows.improvement_graph import run_improvement

router = APIRouter(prefix="/roadmap", tags=["roadmap"])


@router.post("/generate")
async def generate(payload: dict | None = None, user: dict = Depends(get_current_user)) -> dict:
    payload = payload or {}
    try:
        roadmap, rewrites, interview = await run_improvement(
            job_id=payload.get("job_id"),
            target_role=payload.get("target_role", "AI Engineer"),
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"roadmap": roadmap, "cv_rewrite_suggestions": rewrites, "interview": interview}


@router.get("")
async def latest(user: dict = Depends(get_current_user)) -> dict:
    return {"roadmap": repositories.latest_roadmap()}


