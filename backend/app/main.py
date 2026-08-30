"""FastAPI application entrypoint."""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.api.auth import router as auth_router
from app.api.courses import router as courses_router
from app.api.progress import router as progress_router
from app.api.quiz import router as quiz_router
from app.api.tutor import router as tutor_router
from app.core.config import settings

logger = logging.getLogger(__name__)


def _build_cors_origins() -> list[str]:
    """Build the list of allowed CORS origins from settings.

    FRONTEND_URL can be a single URL or a comma-separated list of URLs,
    which is useful when the app is accessed from multiple origins (e.g.
    local dev + production).
    """
    raw = settings.FRONTEND_URL or ""
    origins = [origin.strip().rstrip("/") for origin in raw.split(",") if origin.strip()]
    return origins or ["*"]


app = FastAPI(title="LearnQUIZ API", version="1.0.0")

_cors_origins = _build_cors_origins()

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

app.include_router(auth_router)
app.include_router(courses_router)
app.include_router(progress_router)
app.include_router(quiz_router)
app.include_router(tutor_router)


@app.on_event("startup")
async def _log_startup_info() -> None:
    """Log key configuration values on startup to help debug deployment issues."""
    logger.info("LearnQUIZ API starting up")
    logger.info("CORS allowed origins: %s", _cors_origins)
    logger.info("FRONTEND_URL: %s", settings.FRONTEND_URL)
    logger.info("BACKEND_URL: %s", settings.BACKEND_URL)
    logger.info("Google OAuth configured: %s", bool(settings.GOOGLE_CLIENT_ID))


@app.get("/health")
async def healthcheck() -> dict[str, str]:
    """Expose a simple health endpoint."""

    return {"status": "ok"}


@app.get("/debug/config")
async def debug_config() -> dict:
    """Return non-sensitive config for debugging CORS/OAuth issues in production."""
    return {
        "cors_origins": _cors_origins,
        "frontend_url": settings.FRONTEND_URL,
        "backend_url": settings.BACKEND_URL,
        "google_oauth_configured": bool(settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET),
    }

