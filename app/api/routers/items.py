from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc, func, select

from ...db import session_scope
from ...errors import forbidden, not_found
from ...models import Item
from ...schemas import ItemCreate, ItemOut, ItemUpdate, SortField
from ..deps import get_current_user

router = APIRouter(prefix="/api/v1/items", tags=["items"])


def _labels_to_str(labels: list[str]) -> str:
    return ",".join(labels)


def _labels_from_str(s: str) -> list[str]:
    return [x.strip() for x in (s or "").split(",") if x.strip()]


def to_out(m: Item) -> ItemOut:
    score = m.impact / max(1, m.effort)
    return ItemOut(
        id=m.id,
        title=m.title,
        impact=m.impact,
        effort=m.effort,
        notes=m.notes,
        labels=_labels_from_str(m.labels),
        owner_id=m.owner_id,
        score=score,
        created_at=m.created_at.isoformat(),
        updated_at=m.updated_at.isoformat(),
    )


@router.post("", response_model=ItemOut, status_code=201)
def create_item(payload: ItemCreate, user=Depends(get_current_user)):
    with session_scope() as db:
        m = Item(
            title=payload.title,
            impact=payload.impact,
            effort=payload.effort,
            notes=payload.notes,
            labels=_labels_to_str(payload.labels),
            owner_id=user["id"],
        )
        db.add(m)
        db.flush()
        db.refresh(m)
        return to_out(m)


@router.get("/{item_id}", response_model=ItemOut)
def get_item(item_id: int, user=Depends(get_current_user)):
    with session_scope() as db:
        m = db.get(Item, item_id)
        if not m:
            raise not_found()
        if m.owner_id != user["id"] and user["role"] != "admin":
            raise forbidden()
        return to_out(m)


@router.get("", response_model=list[ItemOut])
def list_items(
    user=Depends(get_current_user),
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
    sort: SortField = "created_at",
    label: str | None = None,
):
    with session_scope() as db:
        q = select(Item).where(
            (Item.owner_id == user["id"]) | (user["role"] == "admin")
        )
        if label:
            q = q.where(func.instr(Item.labels, label) > 0)

        # сортировка
        if sort == "score":
            q = q.order_by((Item.impact / func.nullif(Item.effort, 0)).asc())
        elif sort == "-score":
            q = q.order_by((Item.impact / func.nullif(Item.effort, 0)).desc())
        elif sort == "impact":
            q = q.order_by(Item.impact.asc())
        elif sort == "-impact":
            q = q.order_by(Item.impact.desc())
        elif sort == "effort":
            q = q.order_by(Item.effort.asc())
        elif sort == "-effort":
            q = q.order_by(Item.effort.desc())
        elif sort == "-created_at":
            q = q.order_by(desc(Item.created_at))
        else:
            q = q.order_by(Item.created_at.asc())

        rows = db.execute(q.limit(limit).offset(offset)).scalars().all()
        return [to_out(m) for m in rows]


@router.patch("/{item_id}", response_model=ItemOut)
def update_item(item_id: int, payload: ItemUpdate, user=Depends(get_current_user)):
    with session_scope() as db:
        m = db.get(Item, item_id)
        if not m:
            raise not_found()
        if m.owner_id != user["id"] and user["role"] != "admin":
            raise forbidden()

        if payload.title is not None:
            m.title = payload.title
        if payload.impact is not None:
            m.impact = payload.impact
        if payload.effort is not None:
            m.effort = payload.effort
        if payload.notes is not None:
            m.notes = payload.notes
        if payload.labels is not None:
            m.labels = _labels_to_str(payload.labels)

        m.updated_at = datetime.now(timezone.utc)
        db.add(m)
        db.flush()
        db.refresh(m)
        return to_out(m)


@router.delete("/{item_id}", status_code=204)
def delete_item(item_id: int, user=Depends(get_current_user)):
    with session_scope() as db:
        m = db.get(Item, item_id)
        if not m:
            raise not_found()
        if m.owner_id != user["id"] and user["role"] != "admin":
            raise forbidden()
        db.delete(m)
        return None
