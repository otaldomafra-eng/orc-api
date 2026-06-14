import argparse
import hashlib
from pathlib import Path

from app.caixa.parser import parse_sinapi_package
from app.config import get_settings
from app.db import SessionLocal
from app.services.imports import publish_parsed_file


def main() -> None:
    parser = argparse.ArgumentParser(description="Import an official SINAPI ZIP/XLSX file")
    parser.add_argument("path")
    args = parser.parse_args()

    source_path = Path(args.path)
    content = source_path.read_bytes()
    file_sha256 = hashlib.sha256(content).hexdigest()
    extract_dir = Path(get_settings().sync_storage_dir) / "cli" / file_sha256[:12]
    parsed = parse_sinapi_package(source_path, extract_dir)

    with SessionLocal() as session:
        competencia = publish_parsed_file(
            session,
            parsed,
            source_url=f"file://{source_path.name}",
            source_filename=source_path.name,
            file_sha256=file_sha256,
        )
        session.commit()

    print({"status": "published", "uf": competencia.uf, "ano": competencia.ano, "mes": competencia.mes, "items": len(parsed.items)})


if __name__ == "__main__":
    main()
