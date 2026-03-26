"""Run a single scraper and persist results."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from database import async_session_factory
from models import ScrapeRun
from scrapers import get_scraper
from services.lead_sync import upsert_leads_from_raw


async def run_scrape_job(db: AsyncSession, source: str) -> ScrapeRun:
    scraper = get_scraper(source)
    run = ScrapeRun(source=source, status="running")
    db.add(run)
    await db.commit()
    await db.refresh(run)
    await _execute_scrape(db, run, scraper)
    await db.refresh(run)
    return run


async def _execute_scrape(db: AsyncSession, run: ScrapeRun, scraper) -> None:
    try:
        listings = await scraper.scrape_listings()
        await scraper.aclose()
        _, new_c, upd_c = await upsert_leads_from_raw(db, listings)
        run.status = "completed"
        run.leads_found = len([x for x in listings if x.get("source_url")])
        run.leads_new = new_c
        run.leads_updated = upd_c
    except Exception as e:
        run.status = "failed"
        run.error_message = str(e)[:2000]
    finally:
        run.completed_at = datetime.utcnow()
    await db.commit()


async def run_scrape_job_by_id(run_id: int) -> None:
    """Complete scrape for an existing running run row (own DB session)."""
    async with async_session_factory() as db:
        run = await db.get(ScrapeRun, run_id)
        if not run:
            return
        scraper = get_scraper(run.source)
        await _execute_scrape(db, run, scraper)
