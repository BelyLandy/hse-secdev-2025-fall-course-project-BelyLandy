from __future__ import annotations

from fastapi import Depends, Header


def get_current_user(
    x_user_id: str | None = Header(default=None, alias="X-User-Id"),
    x_user_role: str | None = Header(default="user", alias="X-User-Role"),
):
    user_id = x_user_id or "demo-user"
    role = (x_user_role or "user").lower()
    return {"id": user_id, "role": role}


def admin_only(user=Depends(get_current_user)):
    if user["role"] != "admin":
        from ..errors import forbidden

        raise forbidden()
    return user
