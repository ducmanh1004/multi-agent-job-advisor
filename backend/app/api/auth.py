from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.db.supabase_client import get_supabase_config, supabase_enabled

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me")
async def me(user: dict = Depends(get_current_user)) -> dict:
    config = get_supabase_config()
    return {
        "user": user,
        "supabase_enabled": supabase_enabled(),
        "supabase_url": config.url,
    }


