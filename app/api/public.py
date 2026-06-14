from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session

from app.auth import require_read_key
from app.db import get_db
from app.models import ApiKey, SinapiCompetencia, SinapiItem

router = APIRouter(prefix="/api/v1", tags=["public"])


def decimal_to_float(value: Decimal | None) -> float | None:
    if value is None:
        return None
    return float(value)


def serialize_item(item: SinapiItem) -> dict:
    return {
        "uf": item.uf,
        "ano": item.ano,
        "mes": item.mes,
        "codigo": item.codigo,
        "descricao": item.descricao,
        "tipo": item.tipo,
        "unidade": item.unidade,
        "classe": item.classe,
        "valor_sem_encargos": decimal_to_float(item.valor_sem_encargos),
        "valor_onerado": decimal_to_float(item.valor_onerado),
        "valor_nao_onerado": decimal_to_float(item.valor_nao_onerado),
        "percentual_mao_obra_sem_desoneracao": decimal_to_float(item.percentual_mao_obra_sem_desoneracao),
        "percentual_mao_obra_com_desoneracao": decimal_to_float(item.percentual_mao_obra_com_desoneracao),
    }


@router.get("/competencias")
def list_competencias(
    db: Session = Depends(get_db),
    _: ApiKey = Depends(require_read_key),
) -> list[dict]:
    rows = db.scalars(
        select(SinapiCompetencia)
        .where(SinapiCompetencia.uf == "TO")
        .order_by(SinapiCompetencia.ano.desc(), SinapiCompetencia.mes.desc())
    ).all()
    return [{"uf": row.uf, "ano": row.ano, "mes": row.mes, "ativa": row.ativa} for row in rows]


@router.get("/tabelas")
def list_tabelas(
    db: Session = Depends(get_db),
    _: ApiKey = Depends(require_read_key),
) -> list[dict]:
    return list_competencias(db=db, _=_)


@router.get("/itens")
def list_itens(
    q: str | None = Query(default=None),
    ano: int | None = Query(default=None),
    mes: int | None = Query(default=None),
    tipo: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    _: ApiKey = Depends(require_read_key),
) -> dict:
    filters = [SinapiItem.uf == "TO"]
    if ano is not None:
        filters.append(SinapiItem.ano == ano)
    if mes is not None:
        filters.append(SinapiItem.mes == mes)
    if tipo is not None:
        filters.append(SinapiItem.tipo == tipo.upper())
    if q:
        pattern = f"%{q.upper()}%"
        filters.append(or_(func.upper(SinapiItem.descricao).like(pattern), SinapiItem.codigo == q))

    where_clause = and_(*filters)
    total = db.scalar(select(func.count()).select_from(SinapiItem).where(where_clause)) or 0
    rows = db.scalars(
        select(SinapiItem)
        .where(where_clause)
        .order_by(SinapiItem.ano.desc(), SinapiItem.mes.desc(), SinapiItem.codigo)
        .limit(limit)
        .offset(offset)
    ).all()
    return {"total": total, "limit": limit, "offset": offset, "items": [serialize_item(row) for row in rows]}


@router.get("/itens/{codigo}")
def get_item(
    codigo: str,
    ano: int | None = Query(default=None),
    mes: int | None = Query(default=None),
    db: Session = Depends(get_db),
    _: ApiKey = Depends(require_read_key),
) -> dict:
    filters = [SinapiItem.uf == "TO", SinapiItem.codigo == codigo]
    if ano is not None:
        filters.append(SinapiItem.ano == ano)
    if mes is not None:
        filters.append(SinapiItem.mes == mes)

    item = db.scalar(
        select(SinapiItem)
        .where(and_(*filters))
        .order_by(SinapiItem.ano.desc(), SinapiItem.mes.desc())
        .limit(1)
    )
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return serialize_item(item)


@router.get("/composicoes")
def list_composicoes(
    q: str | None = Query(default=None),
    ano: int | None = Query(default=None),
    mes: int | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    _: ApiKey = Depends(require_read_key),
) -> dict:
    return list_itens(q=q, ano=ano, mes=mes, tipo="COMPOSICAO", limit=limit, offset=offset, db=db, _=_)


@router.get("/composicoes/{codigo}")
def get_composicao(
    codigo: str,
    ano: int | None = Query(default=None),
    mes: int | None = Query(default=None),
    db: Session = Depends(get_db),
    _: ApiKey = Depends(require_read_key),
) -> dict:
    return get_item(codigo=codigo, ano=ano, mes=mes, db=db, _=_)
