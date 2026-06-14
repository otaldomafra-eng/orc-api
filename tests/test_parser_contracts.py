from decimal import Decimal

from app.caixa.parser import ParsedItem, ParsedSinapiFile, parse_decimal


def test_parse_decimal_accepts_brazilian_number() -> None:
    assert parse_decimal("1.234,56") == Decimal("1234.56")


def test_parsed_file_tracks_source_layout() -> None:
    parsed = ParsedSinapiFile(
        uf="TO",
        ano=2026,
        mes=4,
        source_layout="consolidated_xlsx_all_ufs",
        items=[
            ParsedItem(
                codigo="1379",
                descricao="CIMENTO",
                tipo="INSUMO",
                unidade="KG",
                classe="MATERIAL",
                valor_sem_encargos=None,
                valor_onerado=Decimal("1.04"),
                valor_nao_onerado=None,
                raw_data={},
            )
        ],
        composicao_items=[],
    )

    assert parsed.source_layout == "consolidated_xlsx_all_ufs"
    assert parsed.items[0].codigo == "1379"
