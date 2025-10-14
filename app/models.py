from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    impact: Mapped[int] = mapped_column(Integer, nullable=False)  # 1..10
    effort: Mapped[int] = mapped_column(Integer, nullable=False)  # 1..10
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    labels: Mapped[str] = mapped_column(String(255), default="")  # "a,b,c"
    owner_id: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
