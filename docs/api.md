# API

All endpoints are prefixed with `/api`.

CV:

- `POST /cv/upload`: multipart CV upload.
- `POST /cv/text`: parse raw CV text.
- `GET /cv/profile`: latest parsed profile.
- `GET /cv/skills`: extracted CV skills.
- `POST /cv/rewrite`: rewrite CV bullets for a target job.

Crawler and jobs:

- `POST /crawl/run`: run selected crawler adapters.
- `GET /crawl/runs`: crawl history.
- `GET /crawl/errors`: crawl errors.
- `GET /jobs`: list normalized jobs with optional filters.
- `GET /jobs/search?q=...`: search jobs.
- `GET /jobs/sources`: supported sources.
- `POST /jobs/import-csv`: CSV fallback import.

Matching:

- `POST /match/run`: hybrid retrieve, score, rank, and analyze missing skills.
- `GET /match/results`: stored match results.
- `GET /match/{match_id}`: match detail and linked job.

Skills and improvement:

- `GET /skills/missing`
- `GET /skills/market-demand`
- `GET /skills/graph`
- `POST /roadmap/generate`
- `POST /interview/generate`

Observability:

- `GET /agent-traces`
- `GET /agent-traces/{trace_id}`

