from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, crawl, cv, interview, jobs, match, roadmap, skills, traces
from app.core.config import settings
from app.db import repositories
from app.schemas.jobs import CrawlRunRequest
from app.workflows.crawling_graph import run_job_crawling

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    try:
        if not repositories.list_jobs():
            await run_job_crawling(CrawlRunRequest(sources=["csv"], query="", location="Vietnam", limit=100))
    except Exception as exc:
        logger.warning("Could not seed sample jobs: %s", exc)
    yield


app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix=settings.api_prefix)
app.include_router(cv.router, prefix=settings.api_prefix)
app.include_router(crawl.router, prefix=settings.api_prefix)
app.include_router(jobs.router, prefix=settings.api_prefix)
app.include_router(match.router, prefix=settings.api_prefix)
app.include_router(skills.router, prefix=settings.api_prefix)
app.include_router(roadmap.router, prefix=settings.api_prefix)
app.include_router(interview.router, prefix=settings.api_prefix)
app.include_router(traces.router, prefix=settings.api_prefix)


@app.get("/")
async def root() -> dict:
    return {"name": settings.app_name, "docs": "/docs", "health": "/api/health"}


@app.get(f"{settings.api_prefix}/health")
async def health() -> dict:
    return {"status": "ok", "environment": settings.app_env}


@app.get(f"{settings.api_prefix}/dashboard")
async def dashboard() -> dict:
    jobs_list = repositories.list_jobs()
    sources = sorted({job.source for job in jobs_list})
    matches = repositories.list_match_results()
    latest_cv = repositories.latest_cv_profile()
    missing_report = repositories.latest_missing_skill_report()
    traces_list = repositories.list_traces()
    best_score = max((match.match_score for match in matches), default=0)
    return {
        "crawled_jobs": len(jobs_list),
        "platforms": len(sources),
        "sources": sources,
        "latest_cv": latest_cv,
        "best_match_score": best_score,
        "most_common_missing_skills": missing_report.most_common_missing_skills if missing_report else [],
        "recent_agent_traces": traces_list[-8:],
    }

