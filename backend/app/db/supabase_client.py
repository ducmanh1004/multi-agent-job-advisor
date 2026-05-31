from __future__ import annotations

from dataclasses import dataclass

from app.core.config import settings


@dataclass
class SupabaseConfig:
    url: str | None
    anon_key: str | None
    service_role_key: str | None
    storage_bucket: str


def get_supabase_config() -> SupabaseConfig:
    return SupabaseConfig(
        url=settings.supabase_url,
        anon_key=settings.supabase_anon_key,
        service_role_key=settings.supabase_service_role_key,
        storage_bucket=settings.supabase_storage_bucket,
    )


def supabase_enabled() -> bool:
    config = get_supabase_config()
    return bool(config.url and config.anon_key)


