from __future__ import annotations

import re

from app.agents.skill_extractor_agent import extract_skills
from app.core.embeddings import embedding_provider
from app.schemas.cv import CVExperience, CVProfile, CVProject

EMAIL_RE = re.compile(r"[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}")
PHONE_RE = re.compile(r"(\+?\d[\d\s().-]{7,}\d)")


def parse_cv(text: str, user_id: str = "local-user", file_id: str | None = None) -> CVProfile:
    lines = [line.strip() for line in (text or "").splitlines() if line.strip()]
    email_match = EMAIL_RE.search(text or "")
    phone_match = PHONE_RE.search(text or "")
    candidate_name = _guess_name(lines)
    skills = extract_skills(text)
    projects = _extract_projects(lines, text)
    experiences = _extract_experiences(lines)
    years = _guess_years(text)
    profile = CVProfile(
        user_id=user_id,
        file_id=file_id,
        candidate_name=candidate_name,
        email=email_match.group(0) if email_match else None,
        phone=phone_match.group(0) if phone_match else None,
        headline=_guess_headline(lines),
        experience_level=_guess_level(years, text),
        years_experience=years,
        skills=skills,
        projects=projects,
        experiences=experiences,
        raw_text=text[:20000],
    )
    profile.embedding = embedding_provider.embed(profile.summary_text())
    return profile


def _guess_name(lines: list[str]) -> str | None:
    for line in lines[:5]:
        if "@" not in line and len(line.split()) <= 5 and not any(char.isdigit() for char in line):
            return line
    return None


def _guess_headline(lines: list[str]) -> str | None:
    for line in lines[:10]:
        lowered = line.lower()
        if any(role in lowered for role in ["engineer", "developer", "scientist", "intern", "backend", "ai"]):
            return line[:160]
    return None


def _guess_years(text: str) -> float:
    matches = re.findall(r"(\d+(?:\.\d+)?)\+?\s*(?:years|yrs|n\u0103m)", text.lower())
    return max((float(item) for item in matches), default=0.0)


def _guess_level(years: float, text: str) -> str:
    lowered = text.lower()
    if "senior" in lowered or years >= 5:
        return "senior"
    if "middle" in lowered or "mid" in lowered or years >= 2:
        return "middle"
    if "intern" in lowered or "fresher" in lowered:
        return "fresher"
    return "junior"


def _extract_projects(lines: list[str], text: str) -> list[CVProject]:
    projects: list[CVProject] = []
    in_project_section = False
    buffer: list[str] = []
    for line in lines:
        lower = line.lower()
        if "project" in lower or "d\u1ef1 \u00e1n" in lower:
            if buffer:
                projects.append(_project_from_buffer(buffer))
                buffer = []
            in_project_section = True
            if len(line) > 12:
                buffer.append(line)
            continue
        if in_project_section and any(section in lower for section in ["experience", "education", "skills"]):
            break
        if in_project_section:
            buffer.append(line)
            if len(buffer) >= 4:
                projects.append(_project_from_buffer(buffer))
                buffer = []
    if buffer:
        projects.append(_project_from_buffer(buffer))
    if not projects and text:
        projects.append(CVProject(name="CV project evidence", description=text[:500], technologies=[s.name for s in extract_skills(text)[:8]]))
    return projects[:6]


def _project_from_buffer(lines: list[str]) -> CVProject:
    joined = " ".join(lines)
    skills = [skill.name for skill in extract_skills(joined)]
    return CVProject(name=lines[0][:100], description=joined[:800], technologies=skills)


def _extract_experiences(lines: list[str]) -> list[CVExperience]:
    experiences: list[CVExperience] = []
    for line in lines:
        lower = line.lower()
        if any(role in lower for role in ["engineer", "developer", "intern", "ai", "backend"]):
            experiences.append(CVExperience(title=line[:120], description=line[:500]))
        if len(experiences) >= 5:
            break
    return experiences

