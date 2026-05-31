from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.db import repositories
from app.schemas.jobs import CrawlRunRecord, CrawlRunRequest
from app.workflows.crawling_graph import run_job_crawling

router = APIRouter(prefix="/crawl", tags=["crawler"])


@router.post("/run")
async def run_crawl(request: CrawlRunRequest, user: dict = Depends(get_current_user)) -> dict:
    run, jobs = await run_job_crawling(request)
    return {"run": run, "jobs": jobs}


@router.get("/runs", response_model=list[CrawlRunRecord])
async def get_runs(user: dict = Depends(get_current_user)) -> list[CrawlRunRecord]:
    return repositories.list_crawl_runs()


@router.get("/errors")
async def get_errors(user: dict = Depends(get_current_user)) -> dict:
    return {"errors": repositories.list_crawl_errors()}


