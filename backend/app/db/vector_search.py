from __future__ import annotations

from app.core.embeddings import cosine_similarity, embedding_provider
from app.core.reranker import rerank_score
from app.schemas.jobs import JobRecord, JobSearchFilters


def passes_metadata_filters(job: JobRecord, filters: JobSearchFilters | None) -> bool:
    if not filters:
        return True
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


def hybrid_search(
    query: str,
    jobs: list[JobRecord],
    filters: JobSearchFilters | None = None,
    limit: int = 50,
) -> list[tuple[JobRecord, float]]:
    query_embedding = embedding_provider.embed(query)
    scored: list[tuple[JobRecord, float]] = []
    for job in jobs:
        if not passes_metadata_filters(job, filters):
            continue
        base = cosine_similarity(query_embedding, job.embedding or embedding_provider.embed(job.search_text()))
        score = rerank_score(max(base, 0), query, job.search_text(), job.posted_date)
        scored.append((job, round(score, 4)))
    scored.sort(key=lambda item: item[1], reverse=True)
    return scored[:limit]


