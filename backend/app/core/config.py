"""Application settings and database URL helpers."""

from pathlib import Path
from urllib.parse import parse_qsl, quote, urlencode, urlsplit, urlunsplit

from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT_DIR = Path(__file__).parent.parent.parent.parent


def _read_database_url_from_env_file() -> str | None:
    """Fallback reader for .env files that contain a raw Postgres URL line."""

    env_path = ROOT_DIR / ".env"
    if not env_path.exists():
        return None

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith(("postgres://", "postgresql://")):
            return line
    return None


def _quote_url_credentials(url: str) -> str:
    """Percent-encode credentials so special password chars do not break URL parsing."""

    if "://" not in url or "@" not in url:
        return url

    scheme, rest = url.split("://", 1)
    credentials, host_and_path = rest.rsplit("@", 1)
    if ":" not in credentials:
        return url

    username, password = credentials.split(":", 1)
    safe_username = quote(username, safe="%")
    safe_password = quote(password, safe="%")
    return f"{scheme}://{safe_username}:{safe_password}@{host_and_path}"


def _with_query_param(url: str, key: str, value: str) -> str:
    """Add a query parameter only when it is not already present."""

    parts = urlsplit(url)
    query_params = dict(parse_qsl(parts.query, keep_blank_values=True))
    if key not in query_params:
        query_params[key] = value
    query = urlencode(query_params)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, query, parts.fragment))


class Settings(BaseSettings):
    """Load environment variables from the project root .env file."""

    DATABASE_URL: str | None = None
    GEMINI_API_KEY: str | None = None
    SECRET_KEY: str = "change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    GOOGLE_CLIENT_ID: str | None = None
    GOOGLE_CLIENT_SECRET: str | None = None
    BACKEND_URL: str = "http://localhost:8000"
    FRONTEND_URL: str = "http://localhost:5173"

    model_config = SettingsConfigDict(
        env_file=str(ROOT_DIR / ".env"),
        extra="ignore",
    )

    @property
    def sqlalchemy_async_database_url(self) -> str:
        """Return a SQLAlchemy async URL compatible with asyncpg."""

        url = self.DATABASE_URL
        if url is None:
            raise ValueError("DATABASE_URL is missing from the environment configuration.")
        url = _quote_url_credentials(url)
        if url.startswith("postgresql+asyncpg://"):
            async_url = url
        elif url.startswith("postgresql://"):
            async_url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgres://"):
            async_url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        else:
            async_url = url

        parts = urlsplit(async_url)
        query_params = dict(parse_qsl(parts.query, keep_blank_values=True))
        sslmode = query_params.pop("sslmode", None)
        if sslmode and "ssl" not in query_params:
            query_params["ssl"] = "require" if sslmode == "require" else sslmode
        if "supabase.com" in (parts.hostname or "") and "ssl" not in query_params:
            query_params["ssl"] = "require"
        query = urlencode(query_params)
        return urlunsplit((parts.scheme, parts.netloc, parts.path, query, parts.fragment))

    @property
    def sqlalchemy_sync_database_url(self) -> str:
        """Return a SQLAlchemy sync URL compatible with psycopg2."""

        url = self.DATABASE_URL
        if url is None:
            raise ValueError("DATABASE_URL is missing from the environment configuration.")
        url = _quote_url_credentials(url)
        if url.startswith("postgresql+psycopg2://"):
            return _with_query_param(url, "sslmode", "require") if "supabase.com" in url else url
        if url.startswith("postgresql+asyncpg://"):
            sync_url = url.replace("postgresql+asyncpg://", "postgresql+psycopg2://", 1)
            return _with_query_param(sync_url, "sslmode", "require") if "supabase.com" in sync_url else sync_url
        if url.startswith("postgresql://"):
            sync_url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
            return _with_query_param(sync_url, "sslmode", "require") if "supabase.com" in sync_url else sync_url
        if url.startswith("postgres://"):
            sync_url = url.replace("postgres://", "postgresql+psycopg2://", 1)
            return _with_query_param(sync_url, "sslmode", "require") if "supabase.com" in sync_url else sync_url
        return url


settings = Settings()

if settings.DATABASE_URL is None:
    settings.DATABASE_URL = _read_database_url_from_env_file()

if settings.DATABASE_URL is None:
    raise ValueError("DATABASE_URL is missing from the environment configuration.")
