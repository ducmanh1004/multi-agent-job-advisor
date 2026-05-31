# Hybrid Job RAG

The matching pipeline does not ask an LLM to invent scores.

Retrieval:

- Metadata filters: location, salary, level, source, remote policy, and skills.
- Keyword retrieval: token overlap against normalized job search text.
- Dense retrieval: deterministic local embeddings in development, pgvector-ready in Supabase.
- Reranking: combines dense score, keyword score, and freshness.

Scoring:

- 30% skill overlap.
- 25% semantic similarity.
- 20% project relevance.
- 10% experience level match.
- 10% freshness.
- 5% preference match.

LLM usage is isolated behind `core/llm_provider.py` and is intended for explanation text or richer generation, not arbitrary scoring.

