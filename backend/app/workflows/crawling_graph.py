from __future__ import annotations

from datetime import datetime, timezone

from app.agents.job_crawler_agent import collect_jobs
from app.agents.job_normalizer_agent import normalize_job
from app.db import repositories
from app.schemas.jobs import CrawlErrorRecord, CrawlRunRecord, CrawlRunRequest, JobRecord
from app.workflows.base import TraceRecorder


async def run_job_crawling(request: CrawlRunRequest) -> tuple[CrawlRunRecord, list[JobRecord]]:
    run = CrawlRunRecord(sources=request.sources, query=request.query, location=request.location, status="running")
    repositories.save_crawl_run(run)
    recorder = TraceRecorder("job_crawling", entity_id=run.id)
    inserted: list[JobRecord] = []
    errors: list[str] = []
    results = await recorder.run(
        "Job Crawler Agent",
        lambda: collect_jobs(request.sources, request.query, request.location, request.limit),
    )
    raw_jobs = []
    for result in results:
        raw_jobs.extend(result.jobs)
        for error in result.errors:
            errors.append(f"{result.source}: {error}")
            repositories.save_crawl_error(CrawlErrorRecord(run_id=run.id, source=result.source, message=error))
    normalized = await recorder.run("Job Normalizer Agent", lambda: [normalize_job(job) for job in raw_jobs])
    await recorder.run("Skill Extraction Agent", lambda: [job.skills_required for job in normalized])
    for job in normalized:
        saved, was_inserted = repositories.upsert_job(job)
        if was_inserted:
            inserted.append(saved)
    await recorder.run("Deduplication and Job Indexing", lambda: inserted)
    run.jobs_found = len(raw_jobs)
    run.jobs_inserted = len(inserted)
    run.errors = errors
    run.status = "partial" if errors and inserted else "failed" if errors and not inserted else "succeeded"
    run.finished_at = datetime.now(timezone.utc)
    repositories.save_crawl_run(run)
    repositories.save_trace(recorder.trace)
    return run, inserted


