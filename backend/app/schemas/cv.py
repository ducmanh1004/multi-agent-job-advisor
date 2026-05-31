from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from pydantic import BaseModel, Field


class CVSkill(BaseModel):
    name: str
    category: str = "general"
    confidence: float = 0.8


class CVProject(BaseModel):
    name: str
    description: str = ""
    technologies: list[str] = Field(default_factory=list)


class CVExperience(BaseModel):
    title: str
    company: str = ""
    start_date: str | None = None
    end_date: str | None = None
    description: str = ""


class CVProfile(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: str = "local-user"
    file_id: str | None = None
    candidate_name: str | None = None
    email: str | None = None
    phone: str | None = None
    headline: str | None = None
    experience_level: str = "junior"
    years_experience: float = 0
    skills: list[CVSkill] = Field(default_factory=list)
    projects: list[CVProject] = Field(default_factory=list)
    experiences: list[CVExperience] = Field(default_factory=list)
    raw_text: str = ""
    embedding: list[float] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def summary_text(self) -> str:
        skill_text = ", ".join(skill.name for skill in self.skills)
        project_text = " ".join(
            f"{project.name}: {project.description} {' '.join(project.technologies)}"
            for project in self.projects
        )
        experience_text = " ".join(
            f"{item.title} {item.company} {item.description}" for item in self.experiences
        )
        return f"{self.headline or ''} {skill_text} {project_text} {experience_text} {self.raw_text[:2000]}"


class CVFileRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: str = "local-user"
    filename: str
    content_type: str | None = None
    storage_path: str
    size_bytes: int = 0
    uploaded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CVUploadResponse(BaseModel):
    file: CVFileRecord
    profile: CVProfile

