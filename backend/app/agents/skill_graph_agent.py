from __future__ import annotations

SKILL_GRAPH = {
    "LangGraph": {"belongs_to": ["Agent Framework"], "requires": ["Python", "LLM", "Tool Calling"]},
    "RAG": {"requires": ["Embedding", "Vector Search", "Chunking"], "examples": ["LangChain", "LlamaIndex"]},
    "Vector Search": {"examples": ["pgvector", "Qdrant", "Chroma", "FAISS"], "requires": ["Embedding"]},
    "AI Engineer": {"requires": ["Python", "RAG", "FastAPI", "LLM", "Docker"]},
    "Backend AI Engineer": {"requires": ["Docker", "Redis", "PostgreSQL", "Monitoring", "FastAPI"]},
    "Docker": {"belongs_to": ["Deployment"], "requires": ["Linux"]},
    "Monitoring": {"belongs_to": ["Production"], "requires": ["Logging"]},
}


def explain_skill(skill: str) -> str:
    relations = SKILL_GRAPH.get(skill)
    if not relations:
        return f"{skill} appears in matched job descriptions and should be validated against your target role."
    requires = ", ".join(relations.get("requires", []))
    belongs = ", ".join(relations.get("belongs_to", []))
    if requires:
        return f"{skill} is important because it builds on {requires} and is requested by matched roles."
    if belongs:
        return f"{skill} belongs to {belongs}, which helps explain production readiness."
    return f"{skill} is connected to market demand in the skill graph."


def prerequisites_for(skill: str) -> list[str]:
    return SKILL_GRAPH.get(skill, {}).get("requires", [])


