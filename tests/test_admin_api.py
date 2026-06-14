from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth import hash_api_key
from app.db import Base, get_db
from app.main import create_app
from app.models import ApiKey, SinapiImportacao
from tests.test_import_service import create_minimal_reference_xlsx


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
        session.add(
            SinapiImportacao(
                source="CAIXA",
                source_url="https://example.test/sinapi.zip",
                source_layout="legacy_state_specific_pdf",
                status="discovered",
                ano=2016,
                mes=1,
                uf="TO",
            )
        )
        session.commit()

    app = create_app()

    def override_db():
        with TestingSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_db
    return TestClient(app)


def test_importacoes_requires_admin_token() -> None:
    client = build_client()

    response = client.get("/api/v1/admin/importacoes", headers={"Authorization": "Bearer read-token"})

    assert response.status_code == 403


def test_importacoes_returns_recent_imports_for_admin() -> None:
    client = build_client()

    response = client.get("/api/v1/admin/importacoes", headers={"Authorization": "Bearer admin-token"})

    assert response.status_code == 200
    assert response.json()[0]["source_layout"] == "legacy_state_specific_pdf"


def test_sync_status_returns_last_importacao() -> None:
    client = build_client()

    response = client.get("/api/v1/admin/sync/status", headers={"Authorization": "Bearer admin-token"})

    assert response.status_code == 200
    assert response.json()["last_importacao"]["status"] == "discovered"


def test_manual_import_publishes_xlsx(tmp_path) -> None:
    client = build_client()
    xlsx_path = tmp_path / "SINAPI_Referencia_2026_04.xlsx"
    create_minimal_reference_xlsx(xlsx_path)

    with xlsx_path.open("rb") as file:
        response = client.post(
            "/api/v1/admin/importacoes/manual",
            headers={"Authorization": "Bearer admin-token"},
            files={"file": (xlsx_path.name, file, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        )

    assert response.status_code == 200
    assert response.json()["competencia"] == {"uf": "TO", "ano": 2026, "mes": 4}
