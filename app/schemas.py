from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, Field, field_validator


class ErrorResponse(BaseModel):
    code: str
    message: str
    details: dict = Field(default_factory=dict)


class ItemBase(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    impact: int = Field(ge=1, le=10)
    effort: int = Field(ge=1, le=10)
    notes: Optional[str] = None
    labels: List[str] = Field(default_factory=list)

    @field_validator("labels")
    @classmethod
    def validate_labels(cls, v: list[str]) -> list[str]:
        if len(v) > 10 or any(len(x) > 24 for x in v):
            raise ValueError("Max 10 labels, each <= 24 chars")
        return list(dict.fromkeys([s.strip() for s in v if s.strip()]))


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=120)
    impact: Optional[int] = Field(None, ge=1, le=10)
    effort: Optional[int] = Field(None, ge=1, le=10)
    notes: Optional[str] = None
    labels: Optional[list[str]] = None


SortField = Literal[
    "score",
    "-score",
    "created_at",
    "-created_at",
    "impact",
    "-impact",
    "effort",
    "-effort",
]


class ItemOut(ItemBase):
    id: int
    owner_id: str
    score: float
    created_at: str
    updated_at: str
