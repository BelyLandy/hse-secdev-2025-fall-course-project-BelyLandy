from __future__ import annotations

import os
import tempfile
from pathlib import Path
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


def _choose_db_path() -> str:
    env_path = os.getenv("DB_PATH")
    if env_path:
        p = Path(env_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        return str(p)

    for candidate in ("/data/app.db", str(Path.cwd() / "app.db")):
        try:
            Path(candidate).parent.mkdir(parents=True, exist_ok=True)
            return candidate
        except PermissionError:
            continue

    tmp = Path(tempfile.gettempdir()) / "idea-backlog-app.db"
    tmp.parent.mkdir(parents=True, exist_ok=True)
    return str(tmp)


DB_PATH = _choose_db_path()

SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
