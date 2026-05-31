# Backend

FastAPI service for CV analysis, job crawling, normalization, hybrid retrieval, matching, skill gap analysis, roadmap generation, CV rewrite, interview generation, and agent traces.

## Run

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The app seeds sample jobs from `../data/sample_jobs.csv` on startup when local storage has no jobs.

## API Groups

- `POST /api/cv/upload`
- `POST /api/cv/text`
- `GET /api/cv/profile`
- `POST /api/crawl/run`
- `GET /api/jobs`
- `POST /api/jobs/import-csv`
- `POST /api/match/run`
- `GET /api/skills/missing`
- `POST /api/roadmap/generate`
- `POST /api/cv/rewrite`
- `POST /api/interview/generate`
- `GET /api/agent-traces`

## Local Providers

`LLM_PROVIDER=local` and `EMBEDDING_PROVIDER=local` keep the app runnable without keys. The local embedding provider uses deterministic hashed vectors, so hybrid retrieval and scoring work offline.

