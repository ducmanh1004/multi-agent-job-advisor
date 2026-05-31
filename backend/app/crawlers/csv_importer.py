from __future__ import annotations

import csv
from datetime import date
from io import StringIO
from pathlib import Path

from app.crawlers.base import BaseCrawler, CrawlerResult, utcnow
from app.schemas.jobs import RawJob


CSV_COLUMNS = [
    "source",
    "source_url",
    "title",
    "company",
    "location",
    "salary_min",
    "salary_max",
    "currency",
    "level",
    "employment_type",
    "remote_policy",
    "description",
    "requirements",
    "benefits",
    "posted_date",
]


class CSVCrawler(BaseCrawler):
    source = "csv"

    def __init__(self, path: Path | None = None, content: str | None = None) -> None:
        self.path = path
        self.content = content

    async def crawl(self, query: str, location: str, limit: int = 20) -> CrawlerResult:
        try:
            content = self.content if self.content is not None else self.path.read_text(encoding="utf-8")
            jobs = parse_jobs_csv(content)
            if query:
                query_lower = query.lower()
                jobs = [job for job in jobs if query_lower in f"{job.title} {job.description} {job.requirements}".lower()]
            if location and location.lower() != "vietnam":
                jobs = [job for job in jobs if location.lower() in job.location.lower()]
            return CrawlerResult(source=self.source, jobs=jobs[:limit])
        except Exception as exc:
            return CrawlerResult(source=self.source, errors=[str(exc)])


def parse_jobs_csv(content: str) -> list[RawJob]:
    reader = csv.DictReader(StringIO(content))
    rows = []
    for row in reader:
        rows.append(
            RawJob(
                source=row.get("source") or "CSV",
                source_url=row.get("source_url") or "",
                title=row.get("title") or "Untitled job",
                company=row.get("company") or "Unknown company",
                location=row.get("location") or "Vietnam",
                salary_min=_int_or_none(row.get("salary_min")),
                salary_max=_int_or_none(row.get("salary_max")),
                currency=row.get("currency") or "USD",
                level=row.get("level") or "junior",
                employment_type=row.get("employment_type") or "full-time",
                remote_policy=row.get("remote_policy") or "unknown",
                description=row.get("description") or "",
                requirements=row.get("requirements") or "",
                benefits=row.get("benefits") or "",
                posted_date=_date_or_none(row.get("posted_date")),
                crawled_at=utcnow(),
            )
        )
    return rows


def _int_or_none(value: str | None) -> int | None:
    try:
        return int(value) if value else None
    except ValueError:
        return None


def _date_or_none(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


