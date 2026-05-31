from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import httpx

from app.core.config import settings
from app.schemas.jobs import RawJob

logger = logging.getLogger(__name__)


@dataclass
class CrawlerResult:
    source: str
    jobs: list[RawJob] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


class RateLimiter:
    def __init__(self, min_delay_seconds: float) -> None:
        self.min_delay_seconds = min_delay_seconds
        self._last_request = 0.0

    async def wait(self) -> None:
        elapsed = time.monotonic() - self._last_request
        if elapsed < self.min_delay_seconds:
            await asyncio.sleep(self.min_delay_seconds - elapsed)
        self._last_request = time.monotonic()


class RobotsAwareClient:
    def __init__(self) -> None:
        self.rate_limiter = RateLimiter(settings.crawler_min_delay_seconds)
        self._robots_cache: dict[str, RobotFileParser] = {}

    async def allowed(self, url: str) -> bool:
        parsed = urlparse(url)
        origin = f"{parsed.scheme}://{parsed.netloc}"
        if origin not in self._robots_cache:
            robots = RobotFileParser()
            robots_url = f"{origin}/robots.txt"
            try:
                async with httpx.AsyncClient(timeout=settings.crawler_timeout_seconds) as client:
                    response = await client.get(robots_url, headers={"User-Agent": settings.crawler_user_agent})
                robots.parse(response.text.splitlines() if response.status_code < 500 else [])
            except Exception as exc:
                logger.warning("Could not fetch robots.txt for %s: %s", origin, exc)
                robots.parse([])
            self._robots_cache[origin] = robots
        return self._robots_cache[origin].can_fetch(settings.crawler_user_agent, url)

    async def get(self, url: str) -> httpx.Response:
        if not await self.allowed(url):
            raise PermissionError(f"robots.txt disallows crawling {url}")
        await self.rate_limiter.wait()
        last_error: Exception | None = None
        for attempt in range(settings.crawler_max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=settings.crawler_timeout_seconds, follow_redirects=True) as client:
                    response = await client.get(url, headers={"User-Agent": settings.crawler_user_agent})
                response.raise_for_status()
                return response
            except Exception as exc:
                last_error = exc
                await asyncio.sleep(2**attempt)
        raise RuntimeError(f"Failed to crawl {url}: {last_error}") from last_error


class BaseCrawler:
    source = "base"

    async def crawl(self, query: str, location: str, limit: int = 20) -> CrawlerResult:
        raise NotImplementedError


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


