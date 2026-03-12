"""Arborist Training App - FastAPI application."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse
from pathlib import Path

from app.config import BASE_DIR
from app.models import init_db
from app.api.trainings import router as trainings_router
from app.api.auth import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Arborist Training Tracker",
    description="Track trainings and generate Google Slides using ISA, ANSI Z133, and OSHA crane best practices",
    lifespan=lifespan,
)

app.include_router(trainings_router)
app.include_router(auth_router)

# Static files and templates
static_path = BASE_DIR / "static"
templates_path = BASE_DIR / "templates"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")
templates = Jinja2Templates(directory=str(templates_path)) if templates_path.exists() else None


@app.get("/")
def index():
    """Serve the main SPA."""
    index_file = BASE_DIR / "static" / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {"message": "Arborist Training App - add static/index.html for UI"}
