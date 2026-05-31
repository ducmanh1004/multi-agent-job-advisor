from __future__ import annotations

import re
from collections import defaultdict

from app.schemas.cv import CVSkill


SKILL_TAXONOMY: dict[str, list[str]] = {
    "core_ai": [
        "AI",
        "Machine Learning",
        "Deep Learning",
        "LLM",
        "LLM Application",
        "RAG",
        "Vector Search",
        "Embedding",
        "Prompt Engineering",
        "Reranking",
        "LangGraph",
        "LangChain",
        "LlamaIndex",
        "OpenAI",
        "Gemini",
        "Claude",
        "Ollama",
    ],
    "backend": ["Python", "FastAPI", "Django", "Flask", "REST API", "GraphQL", "Pydantic"],
    "data": ["PostgreSQL", "pgvector", "Redis", "Qdrant", "Chroma", "FAISS", "SQL", "ETL"],
    "deployment": ["Docker", "Kubernetes", "CI/CD", "GitHub Actions", "Linux", "Monitoring", "Logging"],
    "frontend": ["React", "Next.js", "TypeScript", "Tailwind CSS"],
    "crawler": ["Playwright", "Crawlee", "BeautifulSoup", "Scrapy", "Selenium"],
}

SYNONYMS = {
    "vector database": "Vector Search",
    "vector db": "Vector Search",
    "semantic search": "Vector Search",
    "retrieval augmented generation": "RAG",
    "large language model": "LLM",
    "restful api": "REST API",
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "nextjs": "Next.js",
    "tailwind": "Tailwind CSS",
    "k8s": "Kubernetes",
}


def normalize_skill(skill: str) -> str:
    key = skill.lower().strip()
    return SYNONYMS.get(key, skill.strip())


def extract_skills(text: str) -> list[CVSkill]:
    text_lower = (text or "").lower()
    found: dict[str, CVSkill] = {}
    for category, skills in SKILL_TAXONOMY.items():
        for skill in skills:
            pattern = r"(?<![a-zA-Z0-9+#.])" + re.escape(skill.lower()) + r"(?![a-zA-Z0-9+#.])"
            if re.search(pattern, text_lower):
                normalized = normalize_skill(skill)
                found[normalized.lower()] = CVSkill(name=normalized, category=category, confidence=0.9)
    for alias, normalized in SYNONYMS.items():
        if alias in text_lower:
            category = category_for(normalized)
            found[normalized.lower()] = CVSkill(name=normalized, category=category, confidence=0.85)
    return sorted(found.values(), key=lambda item: (item.category, item.name))


def category_for(skill: str) -> str:
    for category, skills in SKILL_TAXONOMY.items():
        if skill in skills:
            return category
    return "general"


def group_skills(skills: list[str]) -> dict[str, list[str]]:
    grouped: dict[str, list[str]] = defaultdict(list)
    for skill in skills:
        grouped[category_for(normalize_skill(skill))].append(normalize_skill(skill))
    return dict(grouped)


