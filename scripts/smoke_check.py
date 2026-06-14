import os

import httpx


def main() -> None:
    base_url = os.environ.get("SINAPI_API_URL", "http://127.0.0.1:8088").rstrip("/")
    response = httpx.get(f"{base_url}/health", timeout=10)
    response.raise_for_status()
    print(response.json())


if __name__ == "__main__":
    main()
