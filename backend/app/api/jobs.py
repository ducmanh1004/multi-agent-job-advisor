from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.agents.job_crawler_agent import crawler_for
from app.agents.job_normalizer_agent import normalize_job
from app.agents.job_source_agent import list_sources
from app.api.deps import get_current_user
from app.db import repositories
from app.schemas.jobs import JobRecord, JobSearchFilters

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("", response_model=list[JobRecord])
async def get_jobs(
    q: str | None = None,
    location: str | None = None,
    level: str | None = None,
    source: str | None = None,
    remote_policy: str | None = None,
    skill: str | None = None,
    salary_min: int | None = None,
    user: dict = Depends(get_current_user),
) -> list[JobRecord]:
    filters = JobSearchFilters(
        q=q,
        location=location,
        level=level,
        source=source,
        remote_policy=remote_policy,
        skill=skill,
        salary_min=salary_min,
    )
    jobs = repositories.list_jobs()
    return [job for job in jobs if _matches(job, filters)]


@router.get("/search", response_model=list[JobRecord])
async def search_jobs(q: str, user: dict = Depends(get_current_user)) -> list[JobRecord]:
    filters = JobSearchFilters(q=q)
    return [job for job in repositories.list_jobs() if _matches(job, filters)]


@router.get("/sources")
async def get_sources(user: dict = Depends(get_current_user)) -> dict:
    return {"sources": list_sources()}


@router.post("/import-csv")
async def import_csv(file: UploadFile = File(...), user: dict = Depends(get_current_user)) -> dict:
    content = (await file.read()).decode("utf-8-sig")
    crawler = crawler_for("csv", csv_content=content)
    result = await crawler.crawl(query="", location="Vietnam", limit=500)
    if result.errors:
        raise HTTPException(status_code=400, detail=result.errors)
    inserted = []
    for raw in result.jobs:
        job, was_inserted = repositories.upsert_job(normalize_job(raw))
        if was_inserted:
            inserted.append(job)
    return {"inserted": len(inserted), "jobs": inserted}


@router.get("/{job_id}", response_model=JobRecord)
async def get_job(job_id: str, user: dict = Depends(get_current_user)) -> JobRecord:
    job = repositories.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


def _matches(job: JobRecord, filters: JobSearchFilters) -> bool:
    if filters.q and filters.q.lower() not in job.search_text().lower():
        return False
    if filters.location and filters.location.lower() not in job.location.lower():
        return False
    if filters.level and filters.level.lower() != job.level.lower():
        return False
    if filters.source and filters.source != job.source:
        return False
    if filters.remote_policy and filters.remote_policy != job.remote_policy:
        return False
    if filters.skill:
        skills = {skill.lower() for skill in job.skills_required + job.skills_preferred}
        if filters.skill.lower() not in skills:
            return False
    if filters.salary_min and (job.salary_range.max or 0) < filters.salary_min:
        return False
    return True


