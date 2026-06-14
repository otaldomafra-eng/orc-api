from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Index, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

JsonType = JSON().with_variant(JSONB(), "postgresql")


def utcnow() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


class ApiKey(Base):
    __tablename__ = "api_keys"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    key_hash: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    ativa: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class SinapiImportacao(Base):
    __tablename__ = "sinapi_importacoes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source: Mapped[str] = mapped_column(String(40), nullable=False, default="CAIXA")
    source_url: Mapped[str] = mapped_column(Text, nullable=False)
    source_title: Mapped[str | None] = mapped_column(Text, nullable=True)
    file_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    file_extension: Mapped[str | None] = mapped_column(String(20), nullable=True)
    file_sha256: Mapped[str | None] = mapped_column(String(64), nullable=True)
    source_layout: Mapped[str] = mapped_column(String(60), nullable=False, default="unknown")
    sharepoint_modified_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    downloaded_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="discovered")
    ano: Mapped[int | None] = mapped_column(Integer, nullable=True)
    mes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    uf: Mapped[str | None] = mapped_column(String(2), nullable=True)
    is_retificacao: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_metadata: Mapped[dict | None] = mapped_column(JsonType, nullable=True)


class SinapiCompetencia(Base):
    __tablename__ = "sinapi_competencias"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    uf: Mapped[str] = mapped_column(String(2), nullable=False)
    ano: Mapped[int] = mapped_column(Integer, nullable=False)
    mes: Mapped[int] = mapped_column(Integer, nullable=False)
    importacao_id: Mapped[int] = mapped_column(ForeignKey("sinapi_importacoes.id"), nullable=False)
    publicada_em: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)
    ativa: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    observacao: Mapped[str | None] = mapped_column(Text, nullable=True)

    importacao: Mapped[SinapiImportacao] = relationship()

    __table_args__ = (
        UniqueConstraint("uf", "ano", "mes", "ativa", name="uq_competencia_active_marker"),
        Index("ix_competencias_uf_ano_mes", "uf", "ano", "mes"),
    )


class SinapiItem(Base):
    __tablename__ = "sinapi_itens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    competencia_id: Mapped[int] = mapped_column(ForeignKey("sinapi_competencias.id"), nullable=False)
    uf: Mapped[str] = mapped_column(String(2), nullable=False)
    ano: Mapped[int] = mapped_column(Integer, nullable=False)
    mes: Mapped[int] = mapped_column(Integer, nullable=False)
    codigo: Mapped[str] = mapped_column(String(40), nullable=False)
    descricao: Mapped[str] = mapped_column(Text, nullable=False)
    tipo: Mapped[str] = mapped_column(String(20), nullable=False)
    unidade: Mapped[str | None] = mapped_column(String(30), nullable=True)
    classe: Mapped[str | None] = mapped_column(String(120), nullable=True)
    valor_sem_encargos: Mapped[Decimal | None] = mapped_column(Numeric(18, 6), nullable=True)
    valor_onerado: Mapped[Decimal | None] = mapped_column(Numeric(18, 6), nullable=True)
    valor_nao_onerado: Mapped[Decimal | None] = mapped_column(Numeric(18, 6), nullable=True)
    percentual_mao_obra_sem_desoneracao: Mapped[Decimal | None] = mapped_column(Numeric(18, 6), nullable=True)
    percentual_mao_obra_com_desoneracao: Mapped[Decimal | None] = mapped_column(Numeric(18, 6), nullable=True)
    raw_data: Mapped[dict | None] = mapped_column(JsonType, nullable=True)

    competencia: Mapped[SinapiCompetencia] = relationship()

    __table_args__ = (
        Index("ix_itens_lookup", "uf", "ano", "mes", "codigo"),
        Index("ix_itens_text", "descricao"),
    )


class SinapiComposicaoItem(Base):
    __tablename__ = "sinapi_composicoes_itens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    competencia_id: Mapped[int] = mapped_column(ForeignKey("sinapi_competencias.id"), nullable=False)
    composicao_codigo: Mapped[str] = mapped_column(String(40), nullable=False)
    item_codigo: Mapped[str] = mapped_column(String(40), nullable=False)
    item_descricao: Mapped[str] = mapped_column(Text, nullable=False)
    item_tipo: Mapped[str | None] = mapped_column(String(20), nullable=True)
    unidade: Mapped[str | None] = mapped_column(String(30), nullable=True)
    coeficiente: Mapped[Decimal | None] = mapped_column(Numeric(18, 8), nullable=True)
    valor_sem_encargos: Mapped[Decimal | None] = mapped_column(Numeric(18, 6), nullable=True)
    valor_onerado: Mapped[Decimal | None] = mapped_column(Numeric(18, 6), nullable=True)
    valor_nao_onerado: Mapped[Decimal | None] = mapped_column(Numeric(18, 6), nullable=True)
    raw_data: Mapped[dict | None] = mapped_column(JsonType, nullable=True)

    competencia: Mapped[SinapiCompetencia] = relationship()

    __table_args__ = (
        Index("ix_composicoes_itens_lookup", "competencia_id", "composicao_codigo"),
    )
