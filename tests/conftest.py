import os

os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("API_KEY_PEPPER", "test-pepper")
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
