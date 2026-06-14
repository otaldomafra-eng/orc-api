from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth import hash_api_key
from app.db import Base, get_db
from app.main import create_app
from app.models import ApiKey, SinapiCompetencia, SinapiImportacao, SinapiItem


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
        importacao = SinapiImportacao(
            source="CAIXA",
            source_url="https://example.test/sinapi.zip",
            source_layout="consolidated_xlsx_all_ufs",
            status="published",
            ano=2026,
            mes=4,
            uf="TO",
        )
        session.add(importacao)
        session.flush()
        competencia = SinapiCompetencia(uf="TO", ano=2026, mes=4, importacao_id=importacao.id)
        session.add(competencia)
        session.flush()
        session.add(
            SinapiItem(
                competencia_id=competencia.id,
                uf="TO",
                ano=2026,
                mes=4,
                codigo="1379",
                descricao="CIMENTO PORTLAND COMPOSTO CP II-32",
                tipo="INSUMO",
                unidade="KG",
                valor_onerado=1.04,
                raw_data={},
            )
        )
        session.commit()

    app = create_app()

    def override_db():
        with TestingSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_db
    return TestClient(app)


def test_competencias_requires_auth() -> None:
    client = build_client()

    response = client.get("/api/v1/competencias")

    assert response.status_code == 401


def test_competencias_returns_available_months() -> None:
    client = build_client()

    response = client.get("/api/v1/competencias", headers={"Authorization": "Bearer read-token"})

    assert response.status_code == 200
    assert response.json() == [{"uf": "TO", "ano": 2026, "mes": 4, "ativa": True}]


def test_itens_can_filter_by_text() -> None:
    client = build_client()

    response = client.get(
        "/api/v1/itens?q=cimento",
        headers={"Authorization": "Bearer read-token"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["codigo"] == "1379"


def test_item_detail_returns_latest_matching_code() -> None:
    client = build_client()

    response = client.get("/api/v1/itens/1379", headers={"Authorization": "Bearer read-token"})

    assert response.status_code == 200
    assert response.json()["descricao"] == "CIMENTO PORTLAND COMPOSTO CP II-32"
