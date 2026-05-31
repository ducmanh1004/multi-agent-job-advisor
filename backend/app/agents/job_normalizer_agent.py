from __future__ import annotations

import hashlib
import re

from bs4 import BeautifulSoup

from app.agents.skill_extractor_agent import extract_skills
from app.core.embeddings import embedding_provider
from app.schemas.jobs import JobRecord, RawJob, SalaryRange


def clean_html(value: str) -> str:
    if not value:
        return ""
    text = BeautifulSoup(value, "html.parser").get_text(" ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def normalize_job(raw: RawJob) -> JobRecord:
    description = clean_html(raw.description)
    requirements = clean_html(raw.requirements)
    benefits = clean_html(raw.benefits)
    full_text = f"{raw.title} {description} {requirements}"
    extracted = extract_skills(full_text)
    skills_required = [skill.name for skill in extracted if skill.category != "frontend"]
    skills_preferred = [skill.name for skill in extracted if skill.category == "frontend"]
    content_hash = _hash_job(raw)
    normalized_title = _normalize_title(raw.title)
    domain = _detect_domain(full_text)
    search_vector = f"{normalized_title} {raw.company} {raw.location} {' '.join(skills_required)} {description} {requirements}"
    return JobRecord(
        raw=raw,
        title=raw.title.strip(),
        normalized_title=normalized_title,
        company=raw.company.strip(),
        location=_normalize_location(raw.location),
        level=_normalize_level(raw.level, full_text),
        salary_range=SalaryRange(min=raw.salary_min, max=raw.salary_max, currency=raw.currency),
        employment_type=raw.employment_type,
        remote_policy=raw.remote_policy,
        description=description,
        requirements=requirements,
        benefits=benefits,
        skills_required=skills_required,
        skills_preferred=skills_preferred,
        responsibilities=_extract_responsibilities(description),
        domain=domain,
        source=raw.source,
        source_url=raw.source_url,
        posted_date=raw.posted_date,
        crawled_at=raw.crawled_at,
        content_hash=content_hash,
        search_vector=search_vector,
        embedding=embedding_provider.embed(search_vector),
    )


def _hash_job(raw: RawJob) -> str:
    stable = "|".join([raw.source.lower(), raw.source_url.lower(), raw.title.lower(), raw.company.lower()])
    return hashlib.sha256(stable.encode("utf-8")).hexdigest()


def _normalize_title(title: str) -> str:
    lowered = title.lower()
    if "ai" in lowered or "machine learning" in lowered or "llm" in lowered:
        return "AI Engineer"
    if "backend" in lowered:
        return "Backend Engineer"
    if "data" in lowered:
        return "Data Engineer"
    return title.strip()


def _normalize_level(level: str, text: str) -> str:
    value = f"{level} {text}".lower()
    if "senior" in value or "lead" in value:
        return "senior"
    if "middle" in value or "mid" in value:
        return "middle"
    if "intern" in value or "fresher" in value:
        return "fresher"
    return "junior"


def _normalize_location(location: str) -> str:
    lowered = location.lower()
    if "hanoi" in lowered or "ha noi" in lowered or "h\u00e0 n\u1ed9i" in lowered:
        return "Hanoi"
    if "ho chi minh" in lowered or "hcm" in lowered or "saigon" in lowered or "h\u1ed3 ch\u00ed minh" in lowered:
        return "Ho Chi Minh City"
    if "da nang" in lowered or "\u0111\u00e0 n\u1eb5ng" in lowered:
        return "Da Nang"
    if "remote" in lowered:
        return "Remote"
    return location.strip() or "Vietnam"


def _detect_domain(text: str) -> str:
    lowered = text.lower()
    if any(term in lowered for term in ["rag", "llm", "langchain", "langgraph", "openai"]):
        return "AI/LLM"
    if any(term in lowered for term in ["data pipeline", "etl", "warehouse"]):
        return "Data"
    if any(term in lowered for term in ["fastapi", "django", "backend"]):
        return "Backend"
    return "Software"


def _extract_responsibilities(description: str) -> list[str]:
    chunks = re.split(r"[\n.;]", description)
    return [chunk.strip()[:180] for chunk in chunks if len(chunk.strip()) > 20][:6]

