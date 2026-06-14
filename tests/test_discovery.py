from app.caixa.discovery import discover_candidates_from_sharepoint_rows, infer_source_layout


def test_discovery_extracts_sinapi_candidates_from_sharepoint_rows() -> None:
    rows = [
        {
            "Title": "SINAPI_ref_Insumos_Composicoes_TO_01a062016_v_PDF.zip",
            "Path": "https://www.caixa.gov.br/Downloads/sinapi.zip",
            "FileExtension": "zip",
            "LastModifiedTime": "2024-01-02T10:00:00Z",
            "Description": "SINAPI Tocantins",
        },
        {
            "Title": "Outro arquivo",
            "Path": "https://www.caixa.gov.br/Downloads/outro.zip",
            "FileExtension": "zip",
        },
    ]

    candidates = discover_candidates_from_sharepoint_rows(rows)

    assert len(candidates) == 1
    assert candidates[0].title == "SINAPI_ref_Insumos_Composicoes_TO_01a062016_v_PDF.zip"
    assert candidates[0].source_layout == "legacy_state_specific_pdf"


def test_infer_source_layout_detects_consolidated_xlsx() -> None:
    layout = infer_source_layout("SINAPI_2026_04_formato_xlsx.zip", "Relatorios XLSX todas UF")

    assert layout == "consolidated_xlsx_all_ufs"


def test_infer_source_layout_detects_legacy_to_xlsx() -> None:
    layout = infer_source_layout("SINAPI_ref_Insumos_Composicoes_TO_01a062024_v_XLSX.zip", "")

    assert layout == "legacy_state_specific_xlsx"
