"""
Centralized, immutable application settings.

Every value that could differ between environments — credentials, hosts,
model names, limits — comes from environment variables (via a local .env
file). Nothing is hardcoded. Import `settings` anywhere you need config;
never read `os.environ` directly outside this module.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

load_dotenv()


def _bool(name: str, default: bool) -> bool:
    val = os.getenv(name)
    return default if val is None else val.strip().lower() in {"1", "true", "yes", "on"}


def _int(name: str, default: int) -> int:
    val = os.getenv(name)
    if not val:
        return default
    try:
        return int(val)
    except ValueError:
        return default


@dataclass(frozen=True)
class Settings:
    """Immutable application settings, populated once at import time."""

    # App
    # app_name: str = field(default_factory=lambda: os.getenv("APP_NAME", "AI Insight Studio"))
    # app_env: str = field(default_factory=lambda: os.getenv("APP_ENV", "development"))
    # max_upload_size_mb: int = field(default_factory=lambda: _int("MAX_UPLOAD_MB", 50))
    # supported_file_types: tuple = ("csv", "tsv", "xlsx", "xlsm", "xls")
    
    # App
    app_name: str = field(default_factory=lambda: os.getenv("APP_NAME", "AI Insight Studio"))
    app_env: str = field(default_factory=lambda: os.getenv("APP_ENV", "development"))
    max_upload_size_mb: int = field(default_factory=lambda: _int("MAX_UPLOAD_MB", 50))
    supported_file_types: tuple = ("csv", "tsv", "xlsx", "xlsm", "xls")
    max_context_rows: int = field(default_factory=lambda: _int("MAX_CONTEXT_ROWS", 50))

    # Anthropic
    # anthropic_api_key: str = field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY", ""))
    # anthropic_model: str = field(default_factory=lambda: os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5"))
    # anthropic_max_tokens: int = field(default_factory=lambda: _int("ANTHROPIC_MAX_TOKENS", 1500))
    # anthropic_timeout_seconds: int = field(default_factory=lambda: _int("ANTHROPIC_TIMEOUT_SECONDS", 60))
    # max_context_rows: int = field(default_factory=lambda: _int("MAX_CONTEXT_ROWS", 50))
    
  # Groq
    groq_api_key: str = field(default_factory=lambda: os.getenv("GROQ_API_KEY", ""))
    groq_model: str = field(default_factory=lambda: os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"))
    groq_max_tokens: int = field(default_factory=lambda: _int("GROQ_MAX_TOKENS", 1500))
    groq_timeout_seconds: int = field(default_factory=lambda: _int("GROQ_TIMEOUT_SECONDS", 60))
    

    # MySQL
    mysql_host: str = field(default_factory=lambda: os.getenv("MYSQL_HOST", "localhost"))
    mysql_port: int = field(default_factory=lambda: _int("MYSQL_PORT", 3306))
    mysql_user: str = field(default_factory=lambda: os.getenv("MYSQL_USER", "root"))
    mysql_password: str = field(default_factory=lambda: os.getenv("MYSQL_PASSWORD", ""))
    mysql_database: str = field(default_factory=lambda: os.getenv("MYSQL_DATABASE", "insight_studio"))

    # @property
    # def has_valid_api_key(self) -> bool:
    #     return bool(self.anthropic_api_key)

    @property
    def has_valid_api_key(self) -> bool:
        return bool(self.groq_api_key)
    
    @property
    def mysql_url(self) -> str:
        return (
            f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}?charset=utf8mb4"
        )

    @property
    def mysql_server_url(self) -> str:
        """URL without a database name — used to create the database itself."""
        return (
            f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}"
            f"@{self.mysql_host}:{self.mysql_port}/?charset=utf8mb4"
        )


settings = Settings()
