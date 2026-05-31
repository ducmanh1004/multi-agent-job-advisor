from __future__ import annotations

from app.schemas.cv import CVProfile
from app.schemas.jobs import JobRecord
from app.schemas.matching import CVRewriteSuggestion


def rewrite_cv_bullets(profile: CVProfile, job: JobRecord) -> list[CVRewriteSuggestion]:
    suggestions: list[CVRewriteSuggestion] = []
    evidence_skills = {skill.name for skill in profile.skills}
    target_keywords = [skill for skill in job.skills_required if skill in evidence_skills]
    for project in profile.projects[:3]:
        original = project.description or project.name
        technologies = [tech for tech in project.technologies if tech in target_keywords] or target_keywords[:4]
        if not technologies:
            technologies = project.technologies[:4]
        rewritten = (
            f"Developed {project.name} using {', '.join(technologies) or 'the documented project stack'}, "
            f"aligning with {job.normalized_title} requirements for {job.company}."
        )
        suggestions.append(
            CVRewriteSuggestion(
                target_job=job.normalized_title,
                original_bullet=original[:500],
                rewritten_bullet=rewritten,
                matched_keywords_added=technologies,
            )
        )
    return suggestions


