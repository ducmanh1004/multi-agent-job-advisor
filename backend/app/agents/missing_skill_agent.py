from __future__ import annotations

from collections import Counter

from app.agents.skill_graph_agent import explain_skill
from app.schemas.cv import CVProfile
from app.schemas.matching import MatchResult, MissingSkillItem, MissingSkillReport


def analyze_missing_skills(profile: CVProfile, matches: list[MatchResult]) -> MissingSkillReport:
    counter: Counter[str] = Counter()
    for match in matches:
        counter.update(match.missing_skills)
    items: list[MissingSkillItem] = []
    for skill, count in counter.most_common(10):
        importance = "high" if count >= 3 else "medium" if count >= 2 else "low"
        items.append(
            MissingSkillItem(
                skill=skill,
                count=count,
                importance=importance,
                reason=explain_skill(skill),
            )
        )
    quick_fixes = [
        "Add deployment details to relevant AI/backend projects if true.",
        "Make the backend tech stack explicit in project bullets.",
        "Mention evaluation, latency, logging, or monitoring evidence where available.",
    ]
    return MissingSkillReport(
        cv_profile_id=profile.id,
        most_common_missing_skills=items,
        priority_to_learn=[item.skill for item in items[:5]],
        quick_cv_fixes=quick_fixes,
    )


