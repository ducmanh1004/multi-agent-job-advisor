from __future__ import annotations

from app.agents.hybrid_retrieval_agent import retrieve_jobs
from app.agents.matcher_agent import match_jobs
from app.agents.missing_skill_agent import analyze_missing_skills
from app.core.llm_provider import get_llm_provider
from app.db import repositories
from app.schemas.jobs import JobSearchFilters, UserPreferences
from app.schemas.matching import MatchResult, MissingSkillReport
from app.workflows.base import TraceRecorder


async def run_matching(
    preferences: UserPreferences | None = None,
    filters: JobSearchFilters | None = None,
    limit: int = 10,
) -> tuple[list[MatchResult], MissingSkillReport]:
    profile = repositories.latest_cv_profile()
    if not profile:
        raise ValueError("Upload a CV before running job matching.")
    jobs = repositories.list_jobs()
    recorder = TraceRecorder("job_matching", entity_id=profile.id)
    candidates = await recorder.run("Hybrid Retrieval Agent", lambda: retrieve_jobs(profile, jobs, filters=filters, limit=50))
    ranked_candidates = [job for job, _score in candidates]
    matches = await recorder.run("Matching Agent", lambda: match_jobs(profile, ranked_candidates, preferences=preferences, limit=limit))
    await recorder.run("LLM Explanation Agent", lambda: enrich_match_explanations(matches))
    report = await recorder.run("Missing Skill Analyzer Agent", lambda: analyze_missing_skills(profile, matches))
    repositories.save_match_results(matches)
    repositories.save_missing_skill_report(report)
    repositories.save_trace(recorder.trace)
    return matches, report


async def enrich_match_explanations(matches: list[MatchResult]) -> list[MatchResult]:
    provider = get_llm_provider()
    for match in matches[:5]:
        job = repositories.get_job(match.job_id)
        if not job:
            continue
        prompt = (
            "Explain this job match in Vietnamese. Use only the supplied evidence. "
            "Do not change or invent the score.\n\n"
            f"Job: {job.normalized_title} at {job.company}\n"
            f"Score: {match.match_score}\n"
            f"Matched skills: {', '.join(match.matched_skills) or 'none'}\n"
            f"Missing skills: {', '.join(match.missing_skills) or 'none'}\n"
            f"Score components: {match.score_components}\n"
            f"JD evidence: {job.description[:900]} {job.requirements[:900]}"
        )
        try:
            text = await provider.generate_text(
                system="You are an evidence-based Vietnamese IT/AI job matching advisor.",
                prompt=prompt,
            )
            if text and "Local provider response" not in text:
                match.reason = text.strip()[:1200]
        except Exception:
            continue
    return matches

