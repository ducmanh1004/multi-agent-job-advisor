from __future__ import annotations

from typing import Annotated

from fastapi import Header, HTTPException

from app.core.config import settings


async def get_current_user(authorization: Annotated[str | None, Header()] = None) -> dict[str, str]:
    if settings.app_env in {"local", "development", "test"} and not authorization:
        return {"id": "local-user", "role": "developer"}
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    token = authorization.split(" ", 1)[1]
    if not settings.supabase_jwt_secret:
        return {"id": "supabase-user", "role": "authenticated", "token": token}
    try:
        import jwt

        payload = jwt.decode(token, settings.supabase_jwt_secret, algorithms=["HS256"], audience="authenticated")
    except Exception as exc:
        raise HTTPException(status_code=401, detail=f"Invalid Supabase JWT: {exc}") from exc
    return {"id": payload.get("sub", "supabase-user"), "role": payload.get("role", "authenticated")}


