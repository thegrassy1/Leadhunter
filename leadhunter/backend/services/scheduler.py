"""APScheduler: inbox polling and optional scrape jobs."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.ext.asyncio import async_sessionmaker

from database import async_session_factory
from services.inbox_watcher import InboxWatcher

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()
_schedule_jobs: dict[str, Any] = {}
_inbox_task_running = False


def _run_inbox_poll() -> None:
    global _inbox_task_running
    if _inbox_task_running:
        return

    async def _go() -> None:
        global _inbox_task_running
        _inbox_task_running = True
        try:
            session_factory: async_sessionmaker = async_session_factory
            async with session_factory() as db:
                watcher = InboxWatcher()
                try:
                    await watcher.poll(db)
                except FileNotFoundError:
                    logger.debug("Gmail not configured; skipping inbox poll")
                except Exception as e:
                    logger.warning("Inbox poll failed: %s", e)
        finally:
            _inbox_task_running = False

    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.create_task(_go())
    except RuntimeError:
        asyncio.run(_go())


def start_scheduler(poll_interval_seconds: int = 60) -> None:
    if scheduler.running:
        return
    scheduler.add_job(
        _run_inbox_poll,
        "interval",
        seconds=max(30, poll_interval_seconds),
        id="inbox_poll",
        replace_existing=True,
    )
    scheduler.start()


def stop_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)


def set_scrape_cron(source: str, cron: str, enabled: bool) -> None:
    """Store cron expression like '0 2 * * *' for daily 2am. Simplified: use hour/minute."""
    job_id = f"scrape_{source}"
    if job_id in _schedule_jobs:
        try:
            scheduler.remove_job(job_id)
        except Exception:
            pass
        del _schedule_jobs[job_id]
    if not enabled:
        return
    parts = cron.strip().split()
    if len(parts) >= 2:
        minute, hour = parts[0], parts[1]
    else:
        minute, hour = "0", "2"
    trigger = CronTrigger(minute=minute, hour=hour)

    async def _trigger_scrape() -> None:
        from services.scrape_runner import run_scrape_job

        async with async_session_factory() as db:
            await run_scrape_job(db, source)

    def _job() -> None:
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(_trigger_scrape())
        except Exception:
            asyncio.run(_trigger_scrape())

    scheduler.add_job(_job, trigger, id=job_id, replace_existing=True)
    _schedule_jobs[job_id] = {"source": source, "cron": cron}
