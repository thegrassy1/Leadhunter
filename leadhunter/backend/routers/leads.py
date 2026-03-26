"""Lead CRUD, export, stats."""

from __future__ import annotations

import csv
import io
from typing import Any

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy import Select, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import Lead
from schemas import DashboardStatsOut, ExportRequest, LeadOut, LeadUpdate, PaginatedLeads
from services.scoring import apply_score_to_lead
from services.stats import get_dashboard_stats

router = APIRouter(prefix="/api/leads", tags=["leads"])


def _lead_query(
    q: str | None,
    state: str | None,
    min_score: int | None,
    max_score: int | None,
    status: str | None,
    industry: str | None,
    source: str | None,
    min_revenue: float | None,
    max_revenue: float | None,
) -> Select:
    stmt = select(Lead)
    if q:
        like = f"%{q}%"
        stmt = stmt.where(
            or_(
                Lead.business_name.ilike(like),
                Lead.description.ilike(like),
                Lead.city.ilike(like),
            )
        )
    if state:
        stmt = stmt.where(Lead.state == state.upper())
    if min_score is not None:
        stmt = stmt.where(Lead.lead_score >= min_score)
    if max_score is not None:
        stmt = stmt.where(Lead.lead_score <= max_score)
    if status:
        stmt = stmt.where(Lead.status == status)
    if industry:
        stmt = stmt.where(Lead.industry.ilike(f"%{industry}%"))
    if source:
        stmt = stmt.where(Lead.source == source)
    if min_revenue is not None:
        stmt = stmt.where(
            Lead.annual_revenue.isnot(None), Lead.annual_revenue >= min_revenue
        )
    if max_revenue is not None:
        stmt = stmt.where(
            Lead.annual_revenue.isnot(None), Lead.annual_revenue <= max_revenue
        )
    return stmt


@router.get("", response_model=PaginatedLeads)
async def list_leads(
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=200),
    q: str | None = None,
    state: str | None = None,
    min_score: int | None = None,
    max_score: int | None = None,
    status: str | None = None,
    industry: str | None = None,
    source: str | None = None,
    min_revenue: float | None = None,
    max_revenue: float | None = None,
    sort: str = "lead_score",
    order: str = "desc",
) -> Any:
    base = _lead_query(
        q, state, min_score, max_score, status, industry, source, min_revenue, max_revenue
    )
    count_stmt = select(func.count()).select_from(base.subquery())
    total = (await db.execute(count_stmt)).scalar_one()

    sort_col = getattr(Lead, sort, Lead.lead_score)
    if order.lower() == "asc":
        order_by = sort_col.asc()
    else:
        order_by = sort_col.desc()

    stmt = base.order_by(order_by).offset((page - 1) * page_size).limit(page_size)
    rows = (await db.execute(stmt)).scalars().all()
    return PaginatedLeads(
        items=[LeadOut.model_validate(r) for r in rows],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/stats", response_model=DashboardStatsOut)
async def lead_stats(db: AsyncSession = Depends(get_db)) -> Any:
    return await get_dashboard_stats(db)


@router.post("/export")
async def export_leads(body: ExportRequest, db: AsyncSession = Depends(get_db)) -> Response:
    f = body.filters or {}
    base = _lead_query(
        f.get("q"),
        f.get("state"),
        f.get("min_score"),
        f.get("max_score"),
        f.get("status"),
        f.get("industry"),
        f.get("source"),
        f.get("min_revenue"),
        f.get("max_revenue"),
    )
    rows = (await db.execute(base)).scalars().all()
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(
        [
            "id",
            "business_name",
            "city",
            "state",
            "industry",
            "lead_score",
            "status",
            "source",
            "annual_revenue",
            "asking_price",
        ]
    )
    for r in rows:
        w.writerow(
            [
                r.id,
                r.business_name,
                r.city,
                r.state,
                r.industry,
                r.lead_score,
                r.status,
                r.source,
                r.annual_revenue,
                r.asking_price,
            ]
        )
    return Response(
        content=buf.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="leads.csv"'},
    )


@router.get("/{lead_id}", response_model=LeadOut)
async def get_lead(lead_id: int, db: AsyncSession = Depends(get_db)) -> Any:
    lead = await db.get(Lead, lead_id)
    if not lead:
        from fastapi import HTTPException

        raise HTTPException(404, "Lead not found")
    return LeadOut.model_validate(lead)


@router.patch("/{lead_id}", response_model=LeadOut)
async def patch_lead(
    lead_id: int, body: LeadUpdate, db: AsyncSession = Depends(get_db)
) -> Any:
    lead = await db.get(Lead, lead_id)
    if not lead:
        from fastapi import HTTPException

        raise HTTPException(404, "Lead not found")
    data = body.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(lead, k, v)
    apply_score_to_lead(lead)
    await db.commit()
    await db.refresh(lead)
    return LeadOut.model_validate(lead)
