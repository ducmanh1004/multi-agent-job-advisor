from __future__ import annotations

import json
from datetime import date
from typing import Any
from urllib.parse import quote_plus

from bs4 import BeautifulSoup

from app.crawlers.base import BaseCrawler, CrawlerResult, RobotsAwareClient, utcnow
from app.schemas.jobs import RawJob


class JsonLdJobCrawler(BaseCrawler):
    search_url_template = ""

    def __init__(self) -> None:
        self.client = RobotsAwareClient()

    def build_search_url(self, query: str, location: str) -> str:
        return self.search_url_template.format(query=quote_plus(query), location=quote_plus(location))

    async def crawl(self, query: str, location: str, limit: int = 20) -> CrawlerResult:
        url = self.build_search_url(query, location)
        result = CrawlerResult(source=self.source)
        try:
            response = await self.client.get(url)
            result.jobs = self.extract_jobs(response.text, url)[:limit]
        except Exception as exc:
            result.errors.append(str(exc))
        return result

    def extract_jobs(self, html: str, page_url: str) -> list[RawJob]:
        soup = BeautifulSoup(html, "html.parser")
        jobs: list[RawJob] = []
        for script in soup.find_all("script", {"type": "application/ld+json"}):
            try:
                data = json.loads(script.string or "{}")
            except json.JSONDecodeError:
                continue
            for item in _flatten_jsonld(data):
                if item.get("@type") != "JobPosting":
                    continue
                jobs.append(self._from_jsonld(item, page_url))
        return jobs

    def _from_jsonld(self, item: dict[str, Any], fallback_url: str) -> RawJob:
        org = item.get("hiringOrganization") or {}
        salary = item.get("baseSalary") or {}
        value = salary.get("value") if isinstance(salary, dict) else {}
        location = item.get("jobLocation") or {}
        address = location.get("address") if isinstance(location, dict) else {}
        source_url = item.get("url") or fallback_url
        return RawJob(
            source=self.source,
            source_url=source_url,
            title=item.get("title") or "Untitled job",
            company=org.get("name") if isinstance(org, dict) else "Unknown company",
            location=_location_text(address) or "Vietnam",
            salary_min=_salary_value(value, "minValue"),
            salary_max=_salary_value(value, "maxValue"),
            currency=salary.get("currency", "USD") if isinstance(salary, dict) else "USD",
            level="junior",
            employment_type=item.get("employmentType") or "full-time",
            remote_policy="unknown",
            description=item.get("description") or "",
            requirements=item.get("qualifications") or "",
            benefits=item.get("jobBenefits") or "",
            posted_date=_date_or_none(item.get("datePosted")),
            crawled_at=utcnow(),
        )


def _flatten_jsonld(data: Any) -> list[dict[str, Any]]:
    if isinstance(data, list):
        return [item for entry in data for item in _flatten_jsonld(entry)]
    if isinstance(data, dict) and "@graph" in data:
        return _flatten_jsonld(data["@graph"])
    if isinstance(data, dict):
        return [data]
    return []


def _salary_value(value: Any, key: str) -> int | None:
    if isinstance(value, dict):
        try:
            return int(value.get(key)) if value.get(key) else None
        except (TypeError, ValueError):
            return None
    return None


def _date_or_none(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value[:10])
    except ValueError:
        return None


def _location_text(address: Any) -> str | None:
    if not isinstance(address, dict):
        return None
    return ", ".join(str(address.get(key)) for key in ["addressLocality", "addressRegion"] if address.get(key))


