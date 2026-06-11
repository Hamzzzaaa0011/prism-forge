from __future__ import annotations

import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def normalize_database_uri(uri: str) -> str:
    if uri.startswith("postgres://"):
        return uri.replace("postgres://", "postgresql://", 1)
    return uri


def database_engine_options(uri: str) -> dict:
    if uri.startswith("sqlite"):
        return {}
    return {"pool_pre_ping": True, "pool_recycle": 300}


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-me")
    SQLALCHEMY_DATABASE_URI = normalize_database_uri(
        os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'instance' / 'prism.db'}")
    )
    SQLALCHEMY_ENGINE_OPTIONS = database_engine_options(SQLALCHEMY_DATABASE_URI)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_TIME_LIMIT = None
    REMEMBER_COOKIE_DURATION = timedelta(days=30)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    GROQ_API_KEY = (os.getenv("GROQ_API_KEY") or "").strip()
    PRISM_MODEL = (os.getenv("PRISM_MODEL") or "llama-3.3-70b-versatile").strip()
    RATELIMIT_STORAGE_URI = os.getenv("RATELIMIT_STORAGE_URI", "memory://")
    PRISM_AUTO_CREATE_DB = (os.getenv("PRISM_AUTO_CREATE_DB") or "").lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class TestingConfig(BaseConfig):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    RATELIMIT_ENABLED = False


class ProductionConfig(BaseConfig):
    DEBUG = False
    SESSION_COOKIE_SECURE = True


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
