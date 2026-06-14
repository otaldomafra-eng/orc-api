from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.db import Base
from app.models import SinapiCompetencia, SinapiImportacao, SinapiItem


def test_models_create_monthly_competencia_with_source_layout() -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        importacao = SinapiImportacao(
            source="CAIXA",
            source_url="https://example.test/sinapi.zip",
            file_name="SINAPI_Referencia_2026_04.xlsx",
            file_extension=".xlsx",
            file_sha256="a" * 64,
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

        item = SinapiItem(
            competencia_id=competencia.id,
            uf="TO",
            ano=2026,
            mes=4,
            codigo="1379",
            descricao="CIMENTO PORTLAND COMPOSTO CP II-32",
            tipo="INSUMO",
            unidade="KG",
            valor_onerado=1.04,
            raw_data={"origem": "fixture"},
        )
        session.add(item)
        session.commit()

    with Session(engine) as session:
        saved = session.scalar(select(SinapiImportacao))
        saved_item = session.scalar(select(SinapiItem))

    assert saved is not None
    assert saved.source_layout == "consolidated_xlsx_all_ufs"
    assert saved_item is not None
    assert saved_item.uf == "TO"
    assert saved_item.codigo == "1379"
