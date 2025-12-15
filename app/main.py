from __future__ import annotations

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.exceptions import RequestValidationError
from sqlalchemy import text
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.utils.rfc7807 import problem

from .api.routers import items as items_router
from .db import Base, engine, session_scope
from .security_headers import SecurityHeadersMiddleware

app = FastAPI(title="Idea Backlog (MVP)", version="0.1.0")
app.add_middleware(SecurityHeadersMiddleware)

Base.metadata.create_all(bind=engine)

app.include_router(items_router.router)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return problem(
            404,
            "Not Found",
            "Resource not found",
            type_="about:blank#not-found",
        )
    detail = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
    return problem(
        exc.status_code,
        "HTTP Error",
        detail or "Request failed",
        type_="about:blank#http-error",
    )


@app.exception_handler(HTTPException)
async def fastapi_http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == 404:
        return problem(
            404,
            "Not Found",
            "Resource not found",
            type_="about:blank#not-found",
        )
    detail = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
    return problem(
        exc.status_code,
        "HTTP Error",
        detail or "Request failed",
        type_="about:blank#http-error",
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for e in exc.errors():
        item = dict(e)
        if "ctx" in item and isinstance(item["ctx"], dict) and "error" in item["ctx"]:
            item["ctx"] = {**item["ctx"], "error": str(item["ctx"]["error"])}
        errors.append(item)

    return problem(
        422,
        "Validation Error",
        "Request validation failed",
        type_="about:blank#validation-error",
        extras={"errors": errors},
    )


@app.exception_handler(ValueError)
async def value_error_handler(_: Request, exc: ValueError):
    return problem(400, "Bad Request", str(exc), type_="about:blank#value-error")


@app.exception_handler(Exception)
async def default_handler(request: Request, exc: Exception):
    if isinstance(exc, HTTPException):
        raise exc
    return problem(
        500,
        "Internal Server Error",
        "Unexpected error",
        type_="about:blank#internal-error",
    )


@app.get("/items/{item_id}")
def compat_get_item(item_id: int):
    raise HTTPException(status_code=404, detail="item not found")


@app.post("/items")
def compat_create_item(name: str = Query(..., min_length=1)):
    return {"ok": True, "name": name}


@app.get("/health")
def health():
    with session_scope() as db:
        db.execute(text("SELECT 1"))
    return {"status": "ok"}
