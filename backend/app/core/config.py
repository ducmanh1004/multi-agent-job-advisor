from __future__ import annotations

import os
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    load_dotenv = None

if load_dotenv:
    repo_root = Path(__file__).resolve().parents[3]
    load_dotenv(repo_root / ".env")
    load_dotenv(repo_root / "backend" / ".env", override=False)


def env_first(*names: str, default: str | None = None) -> str | None:
    for name in names:
        value = os.getenv(name)
        if value:
            return value
    return default


class Settings(BaseModel):
    app_name: str = "Multi-Agent Job Discovery & CV Advisor"
    app_env: Literal["local", "development", "production", "test"] = "local"
    api_prefix: str = "/api"
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])

    storage_backend: Literal["local", "supabase"] = "local"
    local_storage_path: Path = Path("backend/data/app_state.json")
    upload_dir: Path = Path("backend/uploads")

    supabase_url: str | None = None
    supabase_anon_key: str | None = None
    supabase_service_role_key: str | None = None
    supabase_jwt_secret: str | None = None
    supabase_storage_bucket: str = "cv-files"

    redis_url: str = "redis://localhost:6379/0"
    llm_provider: Literal["local", "openai", "openrouter", "gemini", "claude", "ollama"] = "local"
    embedding_provider: Literal["local", "openai"] = "local"
    openai_api_key: str | None = None
    openrouter_api_key: str | None = None
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_model_1: str = "nvidia/nemotron-3-super-120b-a12b:free"
    openrouter_model_2: str | None = "poolside/laguna-m.1:free"
    openrouter_site_url: str | None = None
    openrouter_app_name: str = "Multi-Agent Job Advisor"
    gemini_api_key: str | None = None
    anthropic_api_key: str | None = None
    ollama_base_url: str = "http://localhost:11434"
    openai_chat_model: str = "gpt-4.1-mini"
    openai_embedding_model: str = "text-embedding-3-small"

    crawler_user_agent: str = "MultiAgentJobAdvisorBot/0.1 (+contact@example.com)"
    crawler_timeout_seconds: float = 20.0
    crawler_min_delay_seconds: float = 2.0
    crawler_max_retries: int = 2

    @classmethod
    def from_env(cls) -> "Settings":
        origins = os.getenv("CORS_ORIGINS", "http://localhost:3000")
        return cls(
            app_env=os.getenv("APP_ENV", "local"),
            cors_origins=[item.strip() for item in origins.split(",") if item.strip()],
            storage_backend=os.getenv("STORAGE_BACKEND", "local"),
            local_storage_path=Path(os.getenv("LOCAL_STORAGE_PATH", "backend/data/app_state.json")),
            upload_dir=Path(os.getenv("UPLOAD_DIR", "backend/uploads")),
            supabase_url=os.getenv("SUPABASE_URL") or None,
            supabase_anon_key=os.getenv("SUPABASE_ANON_KEY") or None,
            supabase_service_role_key=os.getenv("SUPABASE_SERVICE_ROLE_KEY") or None,
            supabase_jwt_secret=os.getenv("SUPABASE_JWT_SECRET") or None,
            supabase_storage_bucket=os.getenv("SUPABASE_STORAGE_BUCKET", "cv-files"),
            redis_url=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
            llm_provider=os.getenv("LLM_PROVIDER", "local"),
            embedding_provider=os.getenv("EMBEDDING_PROVIDER", "local"),
            openai_api_key=env_first("OPENAI_API_KEY"),
            openrouter_api_key=env_first("OpenRouter_API_KEY", "OPENROUTER_API_KEY"),
            openrouter_base_url=env_first("OpenRouter_BASE_URL", "OPENROUTER_BASE_URL", default="https://openrouter.ai/api/v1")
            or "https://openrouter.ai/api/v1",
            openrouter_model_1=env_first(
                "OpenRouter_model_1",
                "OPENROUTER_MODEL_1",
                "OPENROUTER_MODEL",
                default="nvidia/nemotron-3-super-120b-a12b:free",
            )
            or "nvidia/nemotron-3-super-120b-a12b:free",
            openrouter_model_2=env_first("OpenRouter_model_2", "OPENROUTER_MODEL_2"),
            openrouter_site_url=env_first("OpenRouter_SITE_URL", "OPENROUTER_SITE_URL"),
            openrouter_app_name=env_first("OpenRouter_APP_NAME", "OPENROUTER_APP_NAME", default="Multi-Agent Job Advisor")
            or "Multi-Agent Job Advisor",
            gemini_api_key=os.getenv("GEMINI_API_KEY") or None,
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY") or None,
            ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            openai_chat_model=os.getenv("OPENAI_CHAT_MODEL", "gpt-4.1-mini"),
            openai_embedding_model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
            crawler_user_agent=os.getenv(
                "CRAWLER_USER_AGENT",
                "MultiAgentJobAdvisorBot/0.1 (+contact@example.com)",
            ),
            crawler_timeout_seconds=float(os.getenv("CRAWLER_TIMEOUT_SECONDS", "20")),
            crawler_min_delay_seconds=float(os.getenv("CRAWLER_MIN_DELAY_SECONDS", "2")),
            crawler_max_retries=int(os.getenv("CRAWLER_MAX_RETRIES", "2")),
        )


settings = Settings.from_env()
