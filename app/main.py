import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.database import Base, engine
from app.games.router import router as games_router
from app.pages.router import router as pages_router
from app.stats.router import router as stats_router
from app.users.models import User  # noqa: F401
from app.users.router import router as auth_router


Base.metadata.create_all(bind=engine)

is_production = os.getenv("ENVIRONMENT") == "production"

app = FastAPI(
    title="Морской бой",
    version="0.1.0",
    docs_url=None if is_production else "/docs",
    redoc_url=None if is_production else "/redoc",
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(pages_router)
app.include_router(auth_router)
app.include_router(stats_router)
app.include_router(games_router)


@app.get("/api")
def api_info():
    return {
        "message": "Морской бой API работает",
        "docs": "/docs" if not is_production else None,
    }