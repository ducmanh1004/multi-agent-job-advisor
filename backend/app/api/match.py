from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_current_user
from app.db import repositories
from app.schemas.jobs import UserPreferences
from app.schemas.matching import MatchRunRequest
from app.workflows.matching_graph import run_matching

router = APIRouter(prefix="/match", tags=["matching"])


@router.post("/run")
async def run_match(request: MatchRunRequest, user: dict = Depends(get_current_user)) -> dict:
    preferences = UserPreferences.model_validate(request.preferences or {}) if request.preferences else None
    try:
        matches, report = await run_matching(preferences=preferences, limit=request.limit)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"matches": matches, "missing_skill_report": report}


@router.get("/results")
async def get_results(user: dict = Depends(get_current_user)) -> dict:
    return {"results": repositories.list_match_results()}


@router.get("/{match_id}")
async def get_match(match_id: str, user: dict = Depends(get_current_user)) -> dict:
    for result in repositories.list_match_results():
        if result.id == match_id:
            return {"match": result, "job": repositories.get_job(result.job_id)}
    raise HTTPException(status_code=404, detail="Match not found")


