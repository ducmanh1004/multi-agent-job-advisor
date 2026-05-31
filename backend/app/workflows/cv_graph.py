from __future__ import annotations

from app.agents.cv_parser_agent import parse_cv
from app.core.embeddings import embedding_provider
from app.db import repositories
from app.schemas.cv import CVProfile
from app.workflows.base import TraceRecorder


async def run_cv_analysis(text: str, user_id: str = "local-user", file_id: str | None = None) -> CVProfile:
    recorder = TraceRecorder("cv_analysis", entity_id=file_id)
    profile = await recorder.run("CV Parser Agent", lambda: parse_cv(text, user_id=user_id, file_id=file_id))
    await recorder.run("Skill Extraction from CV", lambda: profile.skills)
    profile.embedding = await recorder.run("Embed CV Summary", lambda: embedding_provider.embed(profile.summary_text()))
    await recorder.run("Store CV Profile", lambda: repositories.save_cv_profile(profile))
    repositories.save_trace(recorder.trace)
    return profile


