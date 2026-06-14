from app.caixa.parser import ParsedSinapiFile
from app.models import SinapiCompetencia, SinapiImportacao, SinapiItem


def publish_parsed_file(
    session,
    parsed: ParsedSinapiFile,
    *,
    source_url: str,
    source_filename: str,
    file_sha256: str | None = None,
) -> SinapiCompetencia:
    importacao = SinapiImportacao(
        source="CAIXA" if source_url.startswith("http") else "MANUAL",
        source_url=source_url,
        file_name=source_filename,
        file_extension="." + source_filename.rsplit(".", 1)[-1].lower() if "." in source_filename else None,
        file_sha256=file_sha256,
        source_layout=parsed.source_layout,
        status="published",
        ano=parsed.ano,
        mes=parsed.mes,
        uf=parsed.uf,
    )
    session.add(importacao)
    session.flush()

    session.query(SinapiCompetencia).filter(
        SinapiCompetencia.uf == parsed.uf,
        SinapiCompetencia.ano == parsed.ano,
        SinapiCompetencia.mes == parsed.mes,
        SinapiCompetencia.ativa.is_(True),
    ).update({"ativa": False})

    competencia = SinapiCompetencia(uf=parsed.uf, ano=parsed.ano, mes=parsed.mes, importacao_id=importacao.id)
    session.add(competencia)
    session.flush()

    for item in parsed.items:
        session.add(
            SinapiItem(
                competencia_id=competencia.id,
                uf=parsed.uf,
                ano=parsed.ano,
                mes=parsed.mes,
                codigo=item.codigo,
                descricao=item.descricao,
                tipo=item.tipo,
                unidade=item.unidade,
                classe=item.classe,
                valor_sem_encargos=item.valor_sem_encargos,
                valor_onerado=item.valor_onerado,
                valor_nao_onerado=item.valor_nao_onerado,
                raw_data=item.raw_data,
            )
        )
    return competencia
