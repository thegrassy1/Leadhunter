"""Email drafts and Gmail send."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import EmailDraft, Lead
from schemas import EmailDraftOut
from services.email_drafter import generate_email_draft
from services.gmail_service import GmailService, send_email_async

router = APIRouter(prefix="/api/outreach", tags=["outreach"])


@router.post("/draft/{lead_id}", response_model=EmailDraftOut)
async def create_draft(
    lead_id: int,
    db: AsyncSession = Depends(get_db),
    template_type: str = "initial_outreach",
) -> Any:
    lead = await db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(404, "Lead not found")
    if not lead.owner_email:
        raise HTTPException(400, "Lead has no owner email")
    data = await generate_email_draft(lead, template_type)
    draft = EmailDraft(
        lead_id=lead.id,
        subject=data.get("subject"),
        body=data.get("body"),
        status="draft",
    )
    db.add(draft)
    await db.commit()
    await db.refresh(draft)
    return EmailDraftOut.model_validate(draft)


@router.get("/drafts", response_model=list[EmailDraftOut])
async def list_drafts(db: AsyncSession = Depends(get_db), limit: int = 100) -> Any:
    rows = (
        await db.execute(select(EmailDraft).order_by(desc(EmailDraft.created_at)).limit(limit))
    ).scalars().all()
    return [EmailDraftOut.model_validate(r) for r in rows]


@router.patch("/draft/{draft_id}", response_model=EmailDraftOut)
async def patch_draft(
    draft_id: int,
    body: dict[str, Any],
    db: AsyncSession = Depends(get_db),
) -> Any:
    d = await db.get(EmailDraft, draft_id)
    if not d:
        raise HTTPException(404, "Draft not found")
    if "subject" in body:
        d.subject = body["subject"]
    if "body" in body:
        d.body = body["body"]
    if "tone" in body:
        d.tone = body["tone"]
    if "status" in body:
        d.status = body["status"]
    await db.commit()
    await db.refresh(d)
    return EmailDraftOut.model_validate(d)


@router.post("/send/{draft_id}", response_model=EmailDraftOut)
async def send_draft(draft_id: int, db: AsyncSession = Depends(get_db)) -> Any:
    d = await db.get(EmailDraft, draft_id)
    if not d:
        raise HTTPException(404, "Draft not found")
    lead = await db.get(Lead, d.lead_id)
    if not lead or not lead.owner_email:
        raise HTTPException(400, "Invalid lead or email")
    svc = GmailService()
    try:
        result = await send_email_async(
            svc,
            lead.owner_email,
            d.subject or "",
            d.body or "",
        )
    except FileNotFoundError:
        raise HTTPException(503, "Gmail credentials not configured")
    d.gmail_message_id = result.get("gmail_message_id")
    d.gmail_thread_id = result.get("gmail_thread_id")
    d.status = "sent"
    d.sent_at = datetime.utcnow()
    lead.status = "contacted"
    lead.last_contacted_at = d.sent_at
    await db.commit()
    await db.refresh(d)
    return EmailDraftOut.model_validate(d)


@router.get("/history/{lead_id}", response_model=list[EmailDraftOut])
async def history(lead_id: int, db: AsyncSession = Depends(get_db)) -> Any:
    rows = (
        await db.execute(
            select(EmailDraft)
            .where(EmailDraft.lead_id == lead_id)
            .order_by(desc(EmailDraft.created_at))
        )
    ).scalars().all()
    return [EmailDraftOut.model_validate(r) for r in rows]
