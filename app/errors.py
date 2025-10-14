from __future__ import annotations

from fastapi import HTTPException, status

from .schemas import ErrorResponse


def http_error(
    code: str, message: str, status_code: int, details: dict | None = None
) -> HTTPException:
    return HTTPException(
        status_code=status_code,
        detail=ErrorResponse(
            code=code, message=message, details=details or {}
        ).model_dump(),
    )


def not_found() -> HTTPException:
    return http_error("NOT_FOUND", "Item not found", status.HTTP_404_NOT_FOUND)


def forbidden() -> HTTPException:
    return http_error("FORBIDDEN", "Forbidden", status.HTTP_403_FORBIDDEN)


def validation_error(msg: str, details: dict | None = None) -> HTTPException:
    return http_error(
        "VALIDATION_ERROR", msg, status.HTTP_422_UNPROCESSABLE_ENTITY, details
    )
