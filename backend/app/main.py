"""FastAPI application entrypoint."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.api.auth import router as auth_router
from app.api.courses import router as courses_router
from app.api.progress import router as progress_router
from app.api.quiz import router as quiz_router
from app.api.tutor import router as tutor_router
from app.core.config import settings


app = FastAPI(title="LearnQUIZ API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
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


@app.get("/health")
async def healthcheck() -> dict[str, str]:
    """Expose a simple health endpoint."""

    return {"status": "ok"}
