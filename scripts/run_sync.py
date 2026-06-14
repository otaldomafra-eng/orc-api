from app.db import SessionLocal


def main() -> None:
    with SessionLocal():
        print({"status": "not_implemented", "detail": "CAIXA sync import will be implemented after parser publication"})


if __name__ == "__main__":
    main()
