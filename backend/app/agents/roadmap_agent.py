from __future__ import annotations

from app.agents.skill_graph_agent import prerequisites_for
from app.schemas.matching import MissingSkillReport, RoadmapPlan, RoadmapWeek


def generate_roadmap(report: MissingSkillReport, target_role: str = "AI Engineer") -> RoadmapPlan:
    priority = report.priority_to_learn or ["Docker", "LangGraph", "PostgreSQL", "Monitoring"]
    weeks: list[RoadmapWeek] = []
    for index in range(4):
        skill = priority[index] if index < len(priority) else ["RAG", "Docker", "pgvector", "Monitoring"][index]
        prereqs = prerequisites_for(skill)
        topics = [skill] + prereqs[:3]
        weeks.append(
            RoadmapWeek(
                week=index + 1,
                focus=f"{skill} for {target_role}",
                topics=topics,
                tasks=[
                    f"Build one small feature that uses {skill}.",
                    "Document before/after evidence that can be added to the CV.",
                    "Add a short evaluation or deployment note.",
                ],
                deliverable=f"Portfolio-ready {skill} artifact with measurable evidence.",
            )
        )
    return RoadmapPlan(
        target_role=target_role,
        goal=f"Improve match quality for {target_role} roles by closing the top market skill gaps.",
        weeks=weeks,
    )


