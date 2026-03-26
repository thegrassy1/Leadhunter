"""Dashboard analytics."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from schemas import DashboardStatsOut
from services.stats import get_dashboard_stats

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStatsOut)
async def dashboard_stats(db: AsyncSession = Depends(get_db)) -> Any:
    return await get_dashboard_stats(db)
