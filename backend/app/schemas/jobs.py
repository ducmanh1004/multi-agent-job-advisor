from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field


RemotePolicy = Literal["remote", "hybrid", "on-site", "unknown"]


class SalaryRange(BaseModel):
    min: int | None = None
    max: int | None = None
    currency: str = "USD"


class RawJob(BaseModel):
    source: str
    source_url: str
    title: str
    company: str
    location: str = "Vietnam"
    salary_min: int | None = None
    salary_max: int | None = None
    currency: str = "USD"
    level: str = "junior"
    employment_type: str = "full-time"
    remote_policy: RemotePolicy = "unknown"
    description: str = ""
    requirements: str = ""
    benefits: str = ""
    posted_date: date | None = None
    crawled_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class JobRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    raw: RawJob
    title: str
    normalized_title: str
    company: str
    location: str
    level: str
    salary_range: SalaryRange = Field(default_factory=SalaryRange)
    employment_type: str = "full-time"
    remote_policy: RemotePolicy = "unknown"
    description: str = ""
    requirements: str = ""
    benefits: str = ""
    skills_required: list[str] = Field(default_factory=list)
    skills_preferred: list[str] = Field(default_factory=list)
    responsibilities: list[str] = Field(default_factory=list)
    domain: str | None = None
    source: str
    source_url: str
    posted_date: date | None = None
    crawled_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    content_hash: str
    search_vector: str = ""
    embedding: list[float] = Field(default_factory=list)

    def search_text(self) -> str:
        return " ".join(
            [
                self.normalized_title,
                self.company,
                self.location,
                self.level,
                self.description,
                self.requirements,
                " ".join(self.skills_required + self.skills_preferred),
                self.domain or "",
            ]
        )


class JobSearchFilters(BaseModel):
    q: str | None = None
    location: str | None = None
    level: str | None = None
    source: str | None = None
    remote_policy: RemotePolicy | None = None
    skill: str | None = None
    salary_min: int | None = None


class UserPreferences(BaseModel):
    locations: list[str] = Field(default_factory=list)
    salary_min: int | None = None
    remote_policy: RemotePolicy | None = None
    sources: list[str] = Field(default_factory=list)
    target_role: str = "AI Engineer"


class CrawlRunRequest(BaseModel):
    sources: list[str] = Field(default_factory=lambda: ["csv"])
    query: str = "AI Engineer"
    location: str = "Vietnam"
    limit: int = 20


class CrawlRunRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    sources: list[str]
    query: str
    location: str
    status: Literal["queued", "running", "succeeded", "failed", "partial"] = "queued"
    jobs_found: int = 0
    jobs_inserted: int = 0
    errors: list[str] = Field(default_factory=list)
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    finished_at: datetime | None = None


class CrawlErrorRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    run_id: str
    source: str
    source_url: str | None = None
    message: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

