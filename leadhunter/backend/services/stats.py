"""Dashboard aggregate queries."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models import InboundEmail, Lead
from schemas import DashboardStatsOut


async def get_dashboard_stats(db: AsyncSession) -> DashboardStatsOut:
    total = (await db.execute(select(func.count()).select_from(Lead))).scalar_one() or 0
    avg = (await db.execute(select(func.avg(Lead.lead_score)))).scalar_one() or 0.0
    week_ago = datetime.utcnow() - timedelta(days=7)
    new_week = (
        await db.execute(select(func.count()).where(Lead.scraped_at >= week_ago))
    ).scalar_one() or 0

    by_status_rows = (
        await db.execute(select(Lead.status, func.count()).group_by(Lead.status))
    ).all()
    leads_by_status = {r[0]: r[1] for r in by_status_rows}

    buckets = []
    for lo in range(0, 100, 10):
        hi = lo + 9
        c = (
            await db.execute(
                select(func.count()).where(
                    Lead.lead_score >= lo, Lead.lead_score <= hi
                )
            )
        ).scalar_one() or 0
        buckets.append({"range": f"{lo}-{hi}", "count": c})

    ind_rows = (
        await db.execute(
            select(Lead.industry, func.count())
            .where(Lead.industry.isnot(None))
            .group_by(Lead.industry)
            .order_by(func.count().desc())
            .limit(12)
        )
    ).all()
    leads_by_industry = [{"industry": r[0] or "Unknown", "count": r[1]} for r in ind_rows]

    geo_rows = (await db.execute(select(Lead.state, func.count()).group_by(Lead.state))).all()
    geography_wi_il = {r[0] or "?": r[1] for r in geo_rows}

    replies = (
        await db.execute(select(func.count()).select_from(InboundEmail))
    ).scalar_one() or 0
    contacted = (
        await db.execute(
            select(func.count()).where(
                Lead.status.in_(["contacted", "follow_up", "replied"])
            )
        )
    ).scalar_one() or 0
    reply_rate = (replies / contacted * 100.0) if contacted else 0.0

    return DashboardStatsOut(
        total_leads=total,
        avg_score=float(avg),
        new_this_week=new_week,
        leads_by_status=leads_by_status,
        score_distribution=buckets,
        leads_by_industry=leads_by_industry,
        geography_wi_il=geography_wi_il,
        replies_received=replies,
        reply_rate_pct=round(reply_rate, 1),
    )
