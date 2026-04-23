import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"


def load_env_file(path=ENV_FILE):
    if not path.exists():
        return

    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def _get_bool(name, default=False):
    value = os.getenv(name)
    if value is None:
        return default

    return value.strip().lower() in {"1", "true", "yes", "on"}


def _split_csv(name, default=""):
    value = os.getenv(name, default)
    return [item.strip() for item in value.split(",") if item.strip()]


load_env_file()


class Config:
    APP_ENV = os.getenv("APP_ENV", "development")
    DEBUG = _get_bool("FLASK_DEBUG", False)
    SECRET_KEY = os.getenv("SECRET_KEY", "")
    DATABASE_PATH = os.getenv("DATABASE_PATH", "loja.db")
    CORS_ORIGINS = _split_csv("CORS_ORIGINS", "")
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "5000"))
