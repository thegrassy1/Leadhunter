"""Scraper trigger, status, history, schedule."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import ScrapeRun
from schemas import ScrapeRunOut, ScraperRunRequest, ScraperScheduleRequest
from services.scheduler import set_scrape_cron
from services.scrape_runner import run_scrape_job_by_id

router = APIRouter(prefix="/api/scraper", tags=["scraper"])


@router.post("/run", response_model=ScrapeRunOut)
async def run_scraper(
    body: ScraperRunRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> Any:
    source = body.source.lower()
    if source not in ("bizbuysell", "bizquest", "businessbroker"):
        raise HTTPException(400, "Invalid source")

    run = ScrapeRun(source=source, status="running")
    db.add(run)
    await db.commit()
    await db.refresh(run)
    background_tasks.add_task(run_scrape_job_by_id, run.id)
    return ScrapeRunOut.model_validate(run)


@router.get("/status")
async def scraper_status(db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    r = (
        await db.execute(select(ScrapeRun).order_by(desc(ScrapeRun.started_at)).limit(1))
    ).scalar_one_or_none()
    if not r:
        return {"running": False, "latest": None}
    running = r.status == "running" and r.completed_at is None
    return {
        "running": running,
        "latest": ScrapeRunOut.model_validate(r).model_dump(),
    }


@router.get("/history", response_model=list[ScrapeRunOut])
async def scraper_history(
    db: AsyncSession = Depends(get_db), limit: int = 50
) -> Any:
    rows = (
        await db.execute(select(ScrapeRun).order_by(desc(ScrapeRun.started_at)).limit(limit))
    ).scalars().all()
    return [ScrapeRunOut.model_validate(r) for r in rows]


@router.post("/schedule")
async def scraper_schedule(body: ScraperScheduleRequest) -> dict[str, str]:
    set_scrape_cron(body.source.lower(), body.cron, body.enabled)
    return {"ok": "true", "source": body.source, "cron": body.cron}
