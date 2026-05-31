from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from pydantic import BaseModel, Field


class MatchResult(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    cv_profile_id: str
    job_id: str
    match_score: float
    rank: int = 0
    matched_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    strong_points: list[str] = Field(default_factory=list)
    weak_points: list[str] = Field(default_factory=list)
    reason: str = ""
    score_components: dict[str, float] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MissingSkillItem(BaseModel):
    skill: str
    count: int
    importance: str
    reason: str


class MissingSkillReport(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    cv_profile_id: str
    most_common_missing_skills: list[MissingSkillItem] = Field(default_factory=list)
    priority_to_learn: list[str] = Field(default_factory=list)
    quick_cv_fixes: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class RoadmapWeek(BaseModel):
    week: int
    focus: str
    topics: list[str]
    tasks: list[str]
    deliverable: str


class RoadmapPlan(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    target_role: str
    duration: str = "4 weeks"
    goal: str
    weeks: list[RoadmapWeek]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CVRewriteSuggestion(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    target_job: str
    original_bullet: str
    rewritten_bullet: str
    matched_keywords_added: list[str]
    warning: str = "Only use this bullet if these technologies were actually used."
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class InterviewQuestion(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    question: str
    skill_tested: str
    expected_answer_points: list[str]
    difficulty: str = "medium"


class InterviewSet(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    target_job: str
    questions: list[InterviewQuestion]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MatchRunRequest(BaseModel):
    limit: int = 10
    preferences: dict | None = None

