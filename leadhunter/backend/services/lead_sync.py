"""Upsert scraped leads and apply scoring."""

from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Lead
from services.scoring import apply_score_to_lead

_LEAD_COLS = {c.key for c in Lead.__table__.columns}


def _filter_lead_fields(raw: dict[str, Any]) -> dict[str, Any]:
    out = {}
    for k, v in raw.items():
        if k in _LEAD_COLS and k != "id":
            out[k] = v
    return out


async def upsert_leads_from_raw(
    db: AsyncSession, raw_list: list[dict[str, Any]]
) -> tuple[int, int, int]:
    """Returns (total_processed, new_count, updated_count)."""
    new_c = 0
    upd_c = 0
    for raw in raw_list:
        su = raw.get("source_url")
        if not su:
            continue
        q = await db.execute(select(Lead).where(Lead.source_url == su))
        existing = q.scalar_one_or_none()
        filtered = _filter_lead_fields(raw)
        if existing:
            for k, v in filtered.items():
                if v is not None:
                    setattr(existing, k, v)
            apply_score_to_lead(existing)
            upd_c += 1
        else:
            lead = Lead(**filtered)
            apply_score_to_lead(lead)
            db.add(lead)
            new_c += 1
    await db.flush()
    return len(raw_list), new_c, upd_c
