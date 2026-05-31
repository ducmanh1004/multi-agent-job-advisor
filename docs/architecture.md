# Architecture

The system is split into a Next.js dashboard and a FastAPI backend.

Backend modules:

- `agents`: CV parsing, crawling orchestration, normalization, skill extraction, retrieval, matching, skill gaps, roadmap, CV rewrite, and interview agents.
- `crawlers`: robots-aware web crawler base, JSON-LD job crawler, platform adapters, and CSV importer.
- `workflows`: traceable workflows for CV analysis, job crawling, matching, and improvements.
- `db`: local JSON repository plus Supabase configuration and vector search helpers.
- `schemas`: Pydantic models shared across API and agents.

The local version uses JSON persistence for a runnable demo. The Supabase migration defines the production tables, pgvector columns, full-text indexes, and trace storage.

