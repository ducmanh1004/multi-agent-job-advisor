from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.api.deps import get_current_user
from app.core.config import settings
from app.db import repositories
from app.schemas.cv import CVFileRecord, CVProfile, CVUploadResponse
from app.services.text_extraction import extract_text
from app.workflows.cv_graph import run_cv_analysis
from app.workflows.improvement_graph import run_improvement

router = APIRouter(prefix="/cv", tags=["cv"])


@router.post("/upload", response_model=CVUploadResponse)
async def upload_cv(file: UploadFile = File(...), user: dict = Depends(get_current_user)) -> CVUploadResponse:
    suffix = Path(file.filename or "cv.txt").suffix.lower()
    if suffix not in {".pdf", ".docx", ".txt", ".md"}:
        raise HTTPException(status_code=400, detail="Only PDF, DOCX, TXT, and MD files are supported.")
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    storage_path = settings.upload_dir / f"{user['id']}-{file.filename}"
    storage_path.write_bytes(content)
    record = CVFileRecord(
        user_id=user["id"],
        filename=file.filename or "cv",
        content_type=file.content_type,
        storage_path=str(storage_path),
        size_bytes=len(content),
    )
    repositories.save_cv_file(record)
    try:
        text = extract_text(storage_path, file.content_type)
    except RuntimeError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    profile = await run_cv_analysis(text, user_id=user["id"], file_id=record.id)
    return CVUploadResponse(file=record, profile=profile)


@router.post("/text", response_model=CVProfile)
async def upload_cv_text(payload: dict, user: dict = Depends(get_current_user)) -> CVProfile:
    text = str(payload.get("text") or "")
    if len(text.strip()) < 20:
        raise HTTPException(status_code=400, detail="CV text is too short.")
    return await run_cv_analysis(text, user_id=user["id"])


@router.get("/profile", response_model=CVProfile | None)
async def get_profile(user: dict = Depends(get_current_user)) -> CVProfile | None:
    return repositories.latest_cv_profile()


@router.get("/skills")
async def get_skills(user: dict = Depends(get_current_user)) -> dict:
    profile = repositories.latest_cv_profile()
    return {"skills": profile.skills if profile else []}


@router.post("/rewrite")
async def rewrite_for_job(payload: dict | None = None, user: dict = Depends(get_current_user)) -> dict:
    payload = payload or {}
    try:
        _roadmap, rewrites, _interview = await run_improvement(
            job_id=payload.get("job_id"),
            target_role=payload.get("target_role", "AI Engineer"),
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"suggestions": rewrites}

