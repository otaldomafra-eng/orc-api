from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from unicodedata import normalize


@dataclass(frozen=True)
class CaixaCandidate:
    title: str
    url: str
    file_extension: str | None
    source_layout: str
    modified_at: datetime | None = None
    description: str | None = None


def normalize_text(value: str | None) -> str:
    if not value:
        return ""
    text = normalize("NFKD", value)
    text = "".join(ch for ch in text if not 0x300 <= ord(ch) <= 0x036F)
    return " ".join(text.upper().replace("-", "_").split())


def parse_sharepoint_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)
    except ValueError:
        return None


def infer_source_layout(title: str, description: str | None = None) -> str:
    text = normalize_text(f"{title} {description or ''}")
    suffix = Path(title).suffix.lower()

    has_to_marker = any(marker in text for marker in ("_TO_", " TO ", "TOCANTINS"))
    mentions_pdf = "PDF" in text or suffix == ".pdf"
    mentions_xlsx = "XLSX" in text or suffix == ".xlsx"

    if has_to_marker and mentions_pdf:
        return "legacy_state_specific_pdf"
    if has_to_marker and mentions_xlsx:
        return "legacy_state_specific_xlsx"
    if mentions_xlsx or "FORMATO_XLSX" in text:
        return "consolidated_xlsx_all_ufs"
    return "unknown"


def discover_candidates_from_sharepoint_rows(rows: list[dict[str, Any]]) -> list[CaixaCandidate]:
    candidates: list[CaixaCandidate] = []
    for row in rows:
        title = str(row.get("Title") or row.get("Filename") or "")
        url = str(row.get("Path") or "")
        description = str(row.get("Description") or "")
        extension = row.get("FileExtension")
        search_text = normalize_text(f"{title} {url} {description}")

        if "SINAPI" not in search_text or not url:
            continue

        layout = infer_source_layout(title, description)
        if layout == "unknown" and "TO" not in search_text and "XLSX" not in search_text:
            continue

        candidates.append(
            CaixaCandidate(
                title=title,
                url=url,
                file_extension=str(extension).lower() if extension else None,
                source_layout=layout,
                modified_at=parse_sharepoint_datetime(row.get("LastModifiedTime")),
                description=description or None,
            )
        )
    return candidates
