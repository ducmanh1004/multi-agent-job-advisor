from __future__ import annotations

from collections import Counter

from fastapi import APIRouter, Depends

from app.agents.skill_extractor_agent import group_skills
from app.agents.skill_graph_agent import SKILL_GRAPH
from app.api.deps import get_current_user
from app.db import repositories

router = APIRouter(prefix="/skills", tags=["skills"])


@router.get("/missing")
async def get_missing(user: dict = Depends(get_current_user)) -> dict:
    return {"report": repositories.latest_missing_skill_report()}


@router.get("/market-demand")
async def get_market_demand(user: dict = Depends(get_current_user)) -> dict:
    counter: Counter[str] = Counter()
    for job in repositories.list_jobs():
        counter.update(job.skills_required + job.skills_preferred)
    return {"skills": [{"skill": skill, "count": count} for skill, count in counter.most_common(30)]}


@router.get("/graph")
async def get_graph(user: dict = Depends(get_current_user)) -> dict:
    nodes = sorted(set(SKILL_GRAPH.keys()) | {item for data in SKILL_GRAPH.values() for values in data.values() for item in values})
    edges = []
    for source, relations in SKILL_GRAPH.items():
        for relation, targets in relations.items():
            for target in targets:
                edges.append({"source": source, "target": target, "relation": relation})
    return {"nodes": nodes, "edges": edges, "groups": group_skills(nodes)}


