from __future__ import annotations

from app.core.embeddings import cosine_similarity, embedding_provider
from app.core.reranker import freshness_score
from app.schemas.cv import CVProfile
from app.schemas.jobs import JobRecord, UserPreferences


def normalize_skill(skill: str) -> str:
    return skill.strip().lower().replace(".", "").replace("-", " ")


def skill_overlap_score(cv_skills: list[str], job_skills: list[str]) -> tuple[float, list[str], list[str]]:
    cv_set = {normalize_skill(skill) for skill in cv_skills}
    job_pairs = [(skill, normalize_skill(skill)) for skill in job_skills]
    matched = [skill for skill, key in job_pairs if key in cv_set]
    missing = [skill for skill, key in job_pairs if key not in cv_set]
    if not job_pairs:
        return 0.0, matched, missing
    return len(matched) / len(job_pairs), matched, missing


def project_relevance(profile: CVProfile, job: JobRecord) -> float:
    job_text = " ".join(
        [
            job.normalized_title,
            job.domain or "",
            " ".join(job.skills_required),
            job.description,
            job.requirements,
        ]
    )
    if not profile.projects:
        return 0.0
    scores = []
    job_embedding = embedding_provider.embed(job_text)
    for project in profile.projects:
        project_text = f"{project.name} {project.description} {' '.join(project.technologies)}"
        scores.append(cosine_similarity(embedding_provider.embed(project_text), job_embedding))
    return max(scores) if scores else 0.0


def level_score(profile: CVProfile, job: JobRecord) -> float:
    order = {"intern": 0, "fresher": 0, "junior": 1, "middle": 2, "mid": 2, "senior": 3, "lead": 4}
    user_level = order.get((profile.experience_level or "junior").lower(), 1)
    job_level = order.get((job.level or "junior").lower(), 1)
    diff = abs(user_level - job_level)
    if diff == 0:
        return 1.0
    if diff == 1:
        return 0.65
    return 0.25


def preference_score(job: JobRecord, preferences: UserPreferences | None) -> float:
    if not preferences:
        return 0.5
    checks = []
    if preferences.locations:
        checks.append(any(location.lower() in job.location.lower() for location in preferences.locations))
    if preferences.remote_policy:
        checks.append(job.remote_policy == preferences.remote_policy)
    if preferences.salary_min:
        checks.append((job.salary_max or 0) >= preferences.salary_min)
    if preferences.sources:
        checks.append(job.source in preferences.sources)
    if not checks:
        return 0.5
    return sum(1 for check in checks if check) / len(checks)


def calculate_match(profile: CVProfile, job: JobRecord, preferences: UserPreferences | None = None) -> dict:
    cv_skills = [skill.name for skill in profile.skills]
    job_skills = job.skills_required + job.skills_preferred
    overlap, matched, missing = skill_overlap_score(cv_skills, job_skills)
    cv_text = profile.summary_text()
    job_text = job.search_text()
    semantic = cosine_similarity(embedding_provider.embed(cv_text), embedding_provider.embed(job_text))
    project = project_relevance(profile, job)
    level = level_score(profile, job)
    freshness = freshness_score(job.posted_date)
    preference = preference_score(job, preferences)

    score = (
        30 * overlap
        + 25 * max(semantic, 0)
        + 20 * max(project, 0)
        + 10 * level
        + 10 * freshness
        + 5 * preference
    )
    return {
        "score": round(min(score, 100), 2),
        "matched_skills": matched,
        "missing_skills": missing,
        "components": {
            "skill_overlap": round(overlap, 3),
            "semantic_similarity": round(max(semantic, 0), 3),
            "project_relevance": round(max(project, 0), 3),
            "experience_level": round(level, 3),
            "freshness": round(freshness, 3),
            "preferences": round(preference, 3),
        },
    }

