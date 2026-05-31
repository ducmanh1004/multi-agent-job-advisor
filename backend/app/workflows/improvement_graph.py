from __future__ import annotations

from app.agents.cv_rewrite_agent import rewrite_cv_bullets
from app.agents.interview_agent import generate_interview
from app.agents.roadmap_agent import generate_roadmap
from app.core.llm_provider import get_llm_provider
from app.db import repositories
from app.schemas.matching import CVRewriteSuggestion, InterviewSet, RoadmapPlan
from app.workflows.base import TraceRecorder


async def run_improvement(job_id: str | None = None, target_role: str = "AI Engineer") -> tuple[RoadmapPlan, list[CVRewriteSuggestion], InterviewSet]:
    profile = repositories.latest_cv_profile()
    if not profile:
        raise ValueError("Upload a CV before generating improvements.")
    report = repositories.latest_missing_skill_report()
    if not report:
        raise ValueError("Run matching before generating improvements.")
    job = repositories.get_job(job_id) if job_id else None
    latest_matches = repositories.latest_match_results(1)
    if job is None and latest_matches:
        job = repositories.get_job(latest_matches[-1].job_id)
    if job is None:
        raise ValueError("No target job is available.")

    recorder = TraceRecorder("improvement", entity_id=job.id)
    roadmap = await recorder.run("Roadmap Agent", lambda: generate_roadmap(report, target_role=target_role))
    rewrites = await recorder.run("CV Rewrite Agent", lambda: rewrite_cv_bullets(profile, job))
    interview = await recorder.run("Interview Agent", lambda: generate_interview(job, latest_matches[-1] if latest_matches else None))
    await recorder.run("LLM Improvement Agent", lambda: enrich_improvement_outputs(roadmap, rewrites, interview))
    repositories.save_roadmap(roadmap)
    for suggestion in rewrites:
        repositories.save_rewrite(suggestion)
    repositories.save_interview(interview)
    repositories.save_trace(recorder.trace)
    return roadmap, rewrites, interview


async def enrich_improvement_outputs(
    roadmap: RoadmapPlan,
    rewrites: list[CVRewriteSuggestion],
    interview: InterviewSet,
) -> tuple[RoadmapPlan, list[CVRewriteSuggestion], InterviewSet]:
    provider = get_llm_provider()
    prompt = (
        "Improve the wording of this candidate guidance in Vietnamese, but do not invent new experience, "
        "new companies, or new technologies. Return concise text only.\n\n"
        f"Roadmap goal: {roadmap.goal}\n"
        f"First rewrite: {rewrites[0].rewritten_bullet if rewrites else ''}\n"
        f"First interview question: {interview.questions[0].question if interview.questions else ''}"
    )
    try:
        text = await provider.generate_text(
            system="You are a strict CV and interview coach for Vietnamese IT/AI candidates.",
            prompt=prompt,
        )
    except Exception:
        return roadmap, rewrites, interview
    if not text or "Local provider response" in text:
        return roadmap, rewrites, interview
    roadmap.goal = f"{roadmap.goal} LLM note: {text.strip()[:500]}"
    return roadmap, rewrites, interview

