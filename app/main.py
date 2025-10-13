from __future__ import annotations

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy import text
from starlette.exceptions import HTTPException as StarletteHTTPException

from .api.routers import items as items_router
from .db import Base, engine, session_scope

app = FastAPI(title="Idea Backlog (MVP)", version="0.1.0")

Base.metadata.create_all(bind=engine)

app.include_router(items_router.router)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return JSONResponse(status_code=404, content={"error": {"code": "not_found"}})

    payload = exc.detail if isinstance(exc.detail, dict) else {"detail": exc.detail}
    return JSONResponse(status_code=exc.status_code, content=payload)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    details = []
    for e in exc.errors():
        item = dict(e)
        if "ctx" in item and isinstance(item["ctx"], dict) and "error" in item["ctx"]:
            item["ctx"] = {**item["ctx"], "error": str(item["ctx"]["error"])}
        details.append(item)

    return JSONResponse(
        status_code=422,
        content={"error": {"code": "validation_error", "details": details}},
    )


@app.get("/items/{item_id}")
def compat_get_item(item_id: int):
    raise HTTPException(status_code=404)


@app.post("/items")
def compat_create_item(name: str = Query(..., min_length=1)):
    return {"ok": True, "name": name}


@app.exception_handler(Exception)
async def default_handler(request: Request, exc: Exception):
    if isinstance(exc, HTTPException):
        raise exc
    return JSONResponse(
        status_code=500,
        content={
            "code": "INTERNAL_ERROR",
            "message": "Unexpected error",
            "details": {},
        },
    )


@app.get("/health")
def health():
    with session_scope() as db:
        db.execute(text("SELECT 1"))
    return {"status": "ok"}
