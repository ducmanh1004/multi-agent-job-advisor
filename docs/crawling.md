# Crawling

Crawler rules implemented in `backend/app/crawlers/base.py`:

- Fetch and respect `robots.txt`.
- Rate limit requests through `CRAWLER_MIN_DELAY_SECONDS`.
- Retry failed requests with exponential backoff.
- Use a configured user agent.
- Never bypass login, CAPTCHA, paywalls, or anti-bot protections.
- Store source URL and crawl timestamp.
- Deduplicate by stable content hash.

The current reliable default is CSV import through `data/sample_jobs.csv` or `POST /api/jobs/import-csv`. Public web adapters use JSON-LD extraction when available and fail safely when blocked or disallowed.

