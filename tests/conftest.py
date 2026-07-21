import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.core.database import Base, get_db
from app.main import app

# In-memory database that persists across a single session using StaticPool
SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    del app.dependency_overrides[get_db]

@pytest.fixture(scope="function", autouse=True)
def patch_worker_db():
    # Patch the worker's SessionLocal to use our test engine
    with patch("app.workers.main.SessionLocal", new=TestingSessionLocal):
        yield

@pytest.fixture(scope="function", autouse=True)
def mock_redis():
    mock = MagicMock()
    with patch("app.api.jobs.redis_client", mock), \
         patch("app.workers.main.redis_client", mock), \
         patch("app.api.monitor.redis_client", mock), \
         patch("app.scheduler.main.redis_client", mock):
        yield mock
