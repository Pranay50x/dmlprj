import os
import time
from typing import Optional

from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL, make_url
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./local.db")


def _is_sqlite(url: str) -> bool:
    return url.startswith("sqlite")


def _ensure_postgres_db(url: str, timeout: int = 30) -> None:
    parsed = make_url(url)
    if not parsed.drivername.startswith("postgresql"):
        return

    target_db = parsed.database
    if not target_db:
        return

    # Build a URL that points to the default 'postgres' database
    admin_url = URL.create(
        drivername=parsed.drivername,
        username=parsed.username,
        password=parsed.password,
        host=parsed.host,
        port=parsed.port,
        database="postgres",
    )

    start = time.time()
    last_exc: Optional[Exception] = None
    while time.time() - start < timeout:
        try:
            admin_engine = create_engine(admin_url)
            with admin_engine.connect() as conn:
                # Check if the target database exists
                exists = conn.execute(
                    text("SELECT 1 FROM pg_database WHERE datname = :d"), {"d": target_db}
                ).scalar()
                if not exists:
                    conn.execute(text(f'CREATE DATABASE "{target_db}"'))
            admin_engine.dispose()
            return
        except OperationalError as exc:
            last_exc = exc
            time.sleep(1)
    if last_exc:
        raise last_exc


connect_args = {}
if _is_sqlite(DATABASE_URL):
    connect_args = {"check_same_thread": False}
else:
    # If using Postgres, ensure the database exists before creating the engine
    try:
        _ensure_postgres_db(DATABASE_URL)
    except Exception:
        # Let the engine creation surface the original error during runtime
        pass


engine = create_engine(DATABASE_URL, pool_pre_ping=True, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
