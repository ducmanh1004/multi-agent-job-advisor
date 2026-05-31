from __future__ import annotations

from app.db.vector_search import hybrid_search
from app.schemas.cv import CVProfile
from app.schemas.jobs import JobRecord, JobSearchFilters


def retrieve_jobs(profile: CVProfile, jobs: list[JobRecord], filters: JobSearchFilters | None = None, limit: int = 50) -> list[tuple[JobRecord, float]]:
    query = profile.summary_text()
    return hybrid_search(query, jobs, filters=filters, limit=limit)


