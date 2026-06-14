import argparse

from app.auth import generate_api_key, hash_api_key
from app.db import SessionLocal
from app.models import ApiKey


def main() -> None:
    parser = argparse.ArgumentParser(description="Create an ORC API key")
    parser.add_argument("--name", required=True)
    parser.add_argument("--role", choices=["read", "admin"], required=True)
    args = parser.parse_args()

    raw_key = generate_api_key()
    with SessionLocal() as session:
        session.add(ApiKey(nome=args.name, role=args.role, key_hash=hash_api_key(raw_key)))
        session.commit()

    print(raw_key)


if __name__ == "__main__":
    main()
