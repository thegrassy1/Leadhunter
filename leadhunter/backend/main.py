"""LeadHunter FastAPI application."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import get_cors_origins, settings
from database import init_db
from routers import dashboard, inbox, leads, outreach, scraper, templates

logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO))
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    from config import DATA_DIR

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    await init_db()
    try:
        from services.scheduler import start_scheduler

        start_scheduler(settings.gmail_poll_interval)
    except Exception as e:
        logger.warning("Scheduler not started: %s", e)
    yield
    try:
        from services.scheduler import stop_scheduler

        stop_scheduler()
    except Exception:
        pass


app = FastAPI(title="LeadHunter API", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(leads.router)
app.include_router(scraper.router)
app.include_router(outreach.router)
app.include_router(dashboard.router)
app.include_router(inbox.router)
app.include_router(templates.router)


@app.get("/api/health")
async def health():
    return {"status": "ok"}
