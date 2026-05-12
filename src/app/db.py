import time
import logging
from typing import Optional

from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL, make_url
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import declarative_base, sessionmaker

logger = logging.getLogger(__name__)

DATABASE_URL = "postgresql+psycopg2://postgres:my-new-password@localhost:5432/postgres"


def _ensure_postgres_db(url: str, timeout: int = 30) -> None:
    parsed = make_url(url)
    if not parsed.drivername.startswith("postgresql"):
        return

    # Only attempt database creation for local/docker Postgres.
    # Managed Postgres providers often disallow connecting to the default
    # 'postgres' database or running CREATE DATABASE, and waiting here can
    # slow down app startup.
    if parsed.host not in {"db", "localhost", "127.0.0.1"}:
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


# If using Postgres, ensure the database exists before creating the engine
try:
    _ensure_postgres_db(DATABASE_URL)
except Exception as exc:
    # Non-fatal: local Postgres may not be ready yet.
    logger.info("Skipping database ensure step: %s", exc)


engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
