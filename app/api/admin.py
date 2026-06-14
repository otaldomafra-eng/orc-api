import hashlib
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.auth import require_admin_key
from app.caixa.parser import parse_sinapi_package
from app.config import get_settings
from app.db import get_db
from app.errors import AppError
from app.models import ApiKey, SinapiCompetencia, SinapiImportacao
from app.services.imports import publish_parsed_file

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


def serialize_importacao(row: SinapiImportacao) -> dict:
    return {
        "id": row.id,
        "source": row.source,
        "source_url": row.source_url,
        "source_title": row.source_title,
        "file_name": row.file_name,
        "file_extension": row.file_extension,
        "file_sha256": row.file_sha256,
        "source_layout": row.source_layout,
        "status": row.status,
        "ano": row.ano,
        "mes": row.mes,
        "uf": row.uf,
        "is_retificacao": row.is_retificacao,
        "error_message": row.error_message,
    }


@router.get("/sync/status")
def sync_status(
    db: Session = Depends(get_db),
    _: ApiKey = Depends(require_admin_key),
) -> dict:
    last_importacao = db.scalar(select(SinapiImportacao).order_by(SinapiImportacao.id.desc()).limit(1))
    last_competencia = db.scalar(
        select(SinapiCompetencia).where(SinapiCompetencia.ativa.is_(True)).order_by(
            SinapiCompetencia.ano.desc(),
            SinapiCompetencia.mes.desc(),
        )
    )
    statuses = db.execute(
        select(SinapiImportacao.status, func.count(SinapiImportacao.id)).group_by(SinapiImportacao.status)
    ).all()
    return {
        "last_importacao": serialize_importacao(last_importacao) if last_importacao else None,
        "last_competencia": {
            "uf": last_competencia.uf,
            "ano": last_competencia.ano,
            "mes": last_competencia.mes,
        }
        if last_competencia
        else None,
        "status_counts": {status: count for status, count in statuses},
    }


@router.get("/importacoes")
def list_importacoes(
    limit: int = 100,
    db: Session = Depends(get_db),
    _: ApiKey = Depends(require_admin_key),
) -> list[dict]:
    rows = db.scalars(select(SinapiImportacao).order_by(SinapiImportacao.id.desc()).limit(min(limit, 500))).all()
    return [serialize_importacao(row) for row in rows]


@router.get("/importacoes/{importacao_id}")
def get_importacao(
    importacao_id: int,
    db: Session = Depends(get_db),
    _: ApiKey = Depends(require_admin_key),
) -> dict:
    row = db.get(SinapiImportacao, importacao_id)
    if row is None:
        return {"error": "not_found"}
    return serialize_importacao(row)


@router.post("/importacoes/manual")
async def manual_importacao(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _: ApiKey = Depends(require_admin_key),
) -> dict:
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in {".zip", ".xlsx"}:
        raise AppError("unsupported_file_layout", "Arquivo manual deve ser ZIP ou XLSX", 400)

    content = await file.read()
    file_sha256 = hashlib.sha256(content).hexdigest()
    storage_dir = Path(get_settings().sync_storage_dir) / "manual" / uuid4().hex
    storage_dir.mkdir(parents=True, exist_ok=True)
    target_path = storage_dir / f"upload{suffix}"
    target_path.write_bytes(content)

    parsed = parse_sinapi_package(target_path, storage_dir / "extract")
    competencia = publish_parsed_file(
        db,
        parsed,
        source_url=f"manual://{file.filename}",
        source_filename=file.filename or target_path.name,
        file_sha256=file_sha256,
    )
    db.commit()
    return {
        "status": "published",
        "competencia": {"uf": competencia.uf, "ano": competencia.ano, "mes": competencia.mes},
        "items": len(parsed.items),
    }


@router.post("/sync/caixa")
def sync_caixa(
    _: ApiKey = Depends(require_admin_key),
) -> dict:
    return {"status": "accepted", "detail": "CAIXA sync discovery will run in the next implementation block"}
