from __future__ import annotations

from app.core.scoring import calculate_match
from app.schemas.cv import CVProfile
from app.schemas.jobs import JobRecord, UserPreferences
from app.schemas.matching import MatchResult


def match_jobs(profile: CVProfile, candidates: list[JobRecord], preferences: UserPreferences | None = None, limit: int = 10) -> list[MatchResult]:
    results: list[MatchResult] = []
    for job in candidates:
        score_data = calculate_match(profile, job, preferences)
        strong_points = _strong_points(job, score_data["matched_skills"])
        weak_points = _weak_points(score_data["missing_skills"])
        results.append(
            MatchResult(
                cv_profile_id=profile.id,
                job_id=job.id,
                match_score=score_data["score"],
                matched_skills=score_data["matched_skills"],
                missing_skills=score_data["missing_skills"],
                strong_points=strong_points,
                weak_points=weak_points,
                reason=_reason(job, score_data["matched_skills"], score_data["missing_skills"]),
                score_components=score_data["components"],
            )
        )
    results.sort(key=lambda item: item.match_score, reverse=True)
    for index, result in enumerate(results[:limit], start=1):
        result.rank = index
    return results[:limit]


def _strong_points(job: JobRecord, matched: list[str]) -> list[str]:
    points = []
    if matched:
        points.append(f"CV matches required skills: {', '.join(matched[:6])}.")
    if job.domain:
        points.append(f"Project evidence is relevant to the {job.domain} domain.")
    if job.remote_policy != "unknown":
        points.append(f"Role preference evidence includes {job.remote_policy} work policy.")
    return points or ["CV has some semantic overlap with this job description."]


def _weak_points(missing: list[str]) -> list[str]:
    if not missing:
        return ["No major missing skill detected from the normalized JD."]
    return [f"Missing or weak evidence for {skill}." for skill in missing[:5]]


def _reason(job: JobRecord, matched: list[str], missing: list[str]) -> str:
    matched_text = ", ".join(matched[:5]) or "semantic project evidence"
    missing_text = ", ".join(missing[:4]) or "no major missing skill"
    return (
        f"{job.normalized_title} at {job.company} is ranked because the CV aligns on {matched_text}. "
        f"The main improvement area is {missing_text}. The score is computed from skill overlap, "
        "semantic similarity, project relevance, level fit, freshness, and preferences."
    )


