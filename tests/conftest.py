import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text


@pytest.fixture(scope="session")
def client():
    from app.main import app
    from app.db import Base, engine

    Base.metadata.create_all(bind=engine)
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE price_tick_features, price_ticks RESTART IDENTITY CASCADE"))

    with TestClient(app) as test_client:
        yield test_client
