from __future__ import annotations

import asyncio
import logging

from app.schemas.jobs import CrawlRunRequest
from app.workflows.crawling_graph import run_job_crawling

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main() -> None:
    logger.info("Worker started. Running scheduled sample crawl once for local development.")
    await run_job_crawling(CrawlRunRequest(sources=["csv"], query="", location="Vietnam", limit=100))


if __name__ == "__main__":
    asyncio.run(main())

