from __future__ import annotations

from pathlib import Path

from app.core.config import settings
from app.crawlers.base import BaseCrawler, CrawlerResult
from app.crawlers.csv_importer import CSVCrawler
from app.crawlers.glints import GlintsCrawler
from app.crawlers.itviec import ITViecCrawler
from app.crawlers.topdev import TopDevCrawler
from app.crawlers.vietnamworks import VietnamWorksCrawler


def crawler_for(source: str, csv_content: str | None = None) -> BaseCrawler:
    key = source.lower()
    if key == "csv":
        sample_path = Path(__file__).resolve().parents[3] / "data" / "sample_jobs.csv"
        return CSVCrawler(path=sample_path, content=csv_content)
    if key == "itviec":
        return ITViecCrawler()
    if key == "topdev":
        return TopDevCrawler()
    if key == "vietnamworks":
        return VietnamWorksCrawler()
    if key == "glints":
        return GlintsCrawler()
    raise ValueError(f"Unsupported or manual-only source: {source}")


async def collect_jobs(sources: list[str], query: str, location: str, limit: int = 20) -> list[CrawlerResult]:
    results: list[CrawlerResult] = []
    per_source_limit = max(1, limit // max(len(sources), 1))
    for source in sources:
        crawler = crawler_for(source)
        results.append(await crawler.crawl(query=query, location=location, limit=per_source_limit))
    return results


