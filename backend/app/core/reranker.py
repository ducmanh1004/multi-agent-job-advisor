from __future__ import annotations

from datetime import date, datetime, timezone

from app.core.embeddings import tokenize


def freshness_score(posted_date: date | None) -> float:
    if not posted_date:
        return 0.35
    today = datetime.now(timezone.utc).date()
    days = max((today - posted_date).days, 0)
    if days <= 7:
        return 1.0
    if days <= 30:
        return 0.8
    if days <= 90:
        return 0.45
    return 0.2


def keyword_score(query: str, document: str) -> float:
    query_tokens = set(tokenize(query))
    doc_tokens = set(tokenize(document))
    if not query_tokens:
        return 0.0
    return len(query_tokens & doc_tokens) / len(query_tokens)


def rerank_score(base_score: float, query: str, document: str, posted_date: date | None) -> float:
    return (0.6 * base_score) + (0.25 * keyword_score(query, document)) + (0.15 * freshness_score(posted_date))

