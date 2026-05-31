# Multi-Agent Job Discovery & CV Advisor

AI-powered job discovery and matching engine for Vietnamese IT/AI jobs.

This repo contains a runnable end-to-end first version:

- FastAPI backend with Pydantic schemas, local JSON storage, Supabase-ready migrations, CV parsing, crawler adapters, hybrid retrieval, deterministic scoring, missing skill analysis, roadmap, CV rewrite, interview generation, and agent traces.
- Next.js App Router frontend with dashboard pages for CV upload, job sources, jobs, matching, skill gap, roadmap, CV improvement, interview, and trace monitoring.
- Docker compose for frontend, backend, worker, and Redis.

## Local Run

```bash
cp .env.example .env
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

In another terminal:

```bash
cd frontend
npm install
npm run dev
```

Open:

- Frontend: `http://localhost:3000`
- Backend docs: `http://localhost:8000/docs`

## Docker Run

```bash
cp .env.example .env
docker compose up --build
```

## First Workflow

1. Open `/upload-cv` and parse the sample CV text or upload a PDF/DOCX/TXT file.
2. Open `/job-sources` and run the CSV crawl.
3. Open `/match` and run matching.
4. Review `/skill-gap`, `/roadmap`, `/cv-improve`, `/interview`, and `/agent-trace`.

## Production Notes

Local mode stores data in `backend/data/app_state.json`. For production, apply `supabase/migrations/001_init.sql`, run `supabase/seed.sql`, set Supabase env vars, set `STORAGE_BACKEND=supabase`, and replace the local repository with Supabase repository methods.

Crawler adapters respect `robots.txt`, use rate limiting, retry/backoff, and do not bypass login, CAPTCHA, paywalls, or anti-bot protections. CSV/manual import remains the fallback for platforms that block crawling.
