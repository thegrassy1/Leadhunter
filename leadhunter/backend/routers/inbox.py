"""Inbound Gmail replies."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import EmailDraft, InboundEmail, Lead
from schemas import InboundEmailOut

router = APIRouter(prefix="/api/inbox", tags=["inbox"])


@router.get("/replies", response_model=list[InboundEmailOut])
async def list_replies(
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    unmatched_only: bool = False,
) -> Any:
    stmt = select(InboundEmail).order_by(desc(InboundEmail.received_at))
    if unmatched_only:
        stmt = stmt.where(InboundEmail.lead_id.is_(None))
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    rows = (await db.execute(stmt)).scalars().all()
    return [InboundEmailOut.model_validate(r) for r in rows]


@router.get("/replies/unread")
async def unread_count(db: AsyncSession = Depends(get_db)) -> dict[str, int]:
    n = (
        await db.execute(
            select(func.count()).where(
                InboundEmail.is_read.is_(False),
            )
        )
    ).scalar_one() or 0
    return {"count": n}


@router.get("/thread/{lead_id}")
async def thread_for_lead(lead_id: int, db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    lead = await db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(404, "Lead not found")
    drafts = (
        await db.execute(
            select(EmailDraft).where(EmailDraft.lead_id == lead_id).order_by(EmailDraft.created_at)
        )
    ).scalars().all()
    inbound = (
        await db.execute(
            select(InboundEmail)
            .where(InboundEmail.lead_id == lead_id)
            .order_by(InboundEmail.received_at)
        )
    ).scalars().all()
    return {
        "lead_id": lead_id,
        "outbound": [
            {
                "type": "sent",
                "subject": d.subject,
                "body": d.body,
                "sent_at": d.sent_at.isoformat() if d.sent_at else None,
            }
            for d in drafts
        ],
        "inbound": [
            {
                "type": "reply",
                "from": e.from_email,
                "subject": e.subject,
                "body": e.body_text,
                "received_at": e.received_at.isoformat() if e.received_at else None,
            }
            for e in inbound
        ],
    }


@router.patch("/reply/{reply_id}/read")
async def mark_read(reply_id: int, db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    e = await db.get(InboundEmail, reply_id)
    if not e:
        raise HTTPException(404, "Reply not found")
    e.is_read = True
    await db.commit()
    return {"ok": "true"}


@router.post("/reply/{reply_id}/link")
async def link_reply(
    reply_id: int, body: dict[str, int], db: AsyncSession = Depends(get_db)
) -> dict[str, str]:
    e = await db.get(InboundEmail, reply_id)
    if not e:
        raise HTTPException(404, "Reply not found")
    lead_id = body.get("lead_id")
    if not lead_id:
        raise HTTPException(400, "lead_id required")
    lead = await db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(404, "Lead not found")
    e.lead_id = lead_id
    await db.commit()
    return {"ok": "true"}
