"""StoryForge FastAPI application entrypoint."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import get_settings
from app.exceptions import (
    AppError,
    app_error_handler,
    http_exception_handler,
    validation_exception_handler,
)
from app.routers import (
    bible,
    chapters,
    characters,
    context_packs,
    genre,
    health,
    power,
    projects,
    prompt_edit,
    twists,
)

settings = get_settings()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    yield


app = FastAPI(
    title=settings.app_title,
    description="AI long-form fiction — canon, continuity, ledgers",
    version=settings.app_version,
    lifespan=lifespan,
)

app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

app.include_router(health.router)
app.include_router(projects.router)
app.include_router(bible.router)
app.include_router(chapters.router)
app.include_router(characters.router)
app.include_router(context_packs.router)
app.include_router(twists.router)
app.include_router(power.router)
app.include_router(genre.router)
app.include_router(prompt_edit.router)
