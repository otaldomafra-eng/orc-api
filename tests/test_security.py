from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth import hash_api_key, require_admin_key, require_read_key
from app.db import Base, get_db
from app.models import ApiKey


def build_client() -> TestClient:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(engine)

    with TestingSessionLocal() as session:
        session.add(ApiKey(nome="read", key_hash=hash_api_key("read-token"), role="read"))
        session.add(ApiKey(nome="admin", key_hash=hash_api_key("admin-token"), role="admin"))
        session.commit()

    app = FastAPI()

    def override_db():
        with TestingSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_db

    @app.get("/protected")
    def protected(_: ApiKey = Depends(require_read_key)) -> dict[str, bool]:
        return {"ok": True}

    @app.get("/admin")
    def admin(_: ApiKey = Depends(require_admin_key)) -> dict[str, bool]:
        return {"ok": True}

    return TestClient(app)


def test_read_endpoint_rejects_missing_token() -> None:
    client = build_client()

    response = client.get("/protected")

    assert response.status_code == 401


def test_read_endpoint_accepts_read_token() -> None:
    client = build_client()

    response = client.get("/protected", headers={"Authorization": "Bearer read-token"})

    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_admin_endpoint_rejects_read_token() -> None:
    client = build_client()

    response = client.get("/admin", headers={"Authorization": "Bearer read-token"})

    assert response.status_code == 403


def test_admin_endpoint_accepts_admin_token() -> None:
    client = build_client()

    response = client.get("/admin", headers={"Authorization": "Bearer admin-token"})

    assert response.status_code == 200
