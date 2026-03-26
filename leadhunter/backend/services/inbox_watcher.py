"""Poll Gmail and match inbound mail to leads."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import EmailDraft, GmailSyncState, InboundEmail, Lead, Notification
from services.gmail_service import GmailService, check_for_replies_async


def _parse_from_email(from_hdr: str | None) -> str:
    if not from_hdr:
        return ""
    if "<" in from_hdr and ">" in from_hdr:
        start = from_hdr.index("<") + 1
        end = from_hdr.index(">")
        return from_hdr[start:end].strip().lower()
    return from_hdr.strip().lower()


class InboxWatcher:
    POLL_INTERVAL_SECONDS = 60

    def __init__(self, gmail: GmailService | None = None) -> None:
        self.gmail = gmail or GmailService()

    async def poll(self, db: AsyncSession) -> int:
        """Fetch new messages, upsert inbound_emails, match leads. Returns count new."""
        try:
            sync = await db.get(GmailSyncState, 1)
        except Exception:
            sync = None
        last_history_id = sync.last_history_id if sync else None

        try:
            new_emails, new_history_id = await check_for_replies_async(
                self.gmail, last_history_id
            )
        except Exception:
            return 0

        count = 0
        for email in new_emails:
            mid = email.get("gmail_message_id")
            if not mid:
                continue
            existing = await db.execute(
                select(InboundEmail).where(InboundEmail.gmail_message_id == mid)
            )
            if existing.scalar_one_or_none():
                continue

            thread_id = email.get("gmail_thread_id")
            lead = None
            if thread_id:
                q = await db.execute(
                    select(Lead)
                    .join(EmailDraft, EmailDraft.lead_id == Lead.id)
                    .where(EmailDraft.gmail_thread_id == thread_id)
                    .limit(1)
                )
                lead = q.scalar_one_or_none()
            if not lead:
                fe = _parse_from_email(email.get("from_email"))
                if fe:
                    q2 = await db.execute(
                        select(Lead).where(
                            Lead.owner_email.isnot(None),
                            Lead.owner_email.ilike(f"%{fe}%"),
                        )
                    )
                    lead = q2.scalars().first()

            received = None
            rd = email.get("received_at")
            if rd:
                try:
                    ms = int(rd) / 1000.0
                    received = datetime.utcfromtimestamp(ms)
                except Exception:
                    received = datetime.utcnow()

            inbound = InboundEmail(
                lead_id=lead.id if lead else None,
                gmail_message_id=mid,
                gmail_thread_id=thread_id,
                from_email=email.get("from_email"),
                from_name=email.get("from_name"),
                subject=email.get("subject"),
                body_text=email.get("body_text"),
                body_snippet=email.get("body_snippet"),
                received_at=received,
                is_read=False,
            )
            db.add(inbound)
            count += 1

            if lead:
                lead.status = "replied"
                db.add(
                    Notification(
                        type="reply_received",
                        message=f"Reply from {lead.business_name or 'contact'}: {email.get('body_snippet', '')[:120]}",
                        lead_id=lead.id,
                    )
                )

        if new_history_id:
            if not sync:
                sync = GmailSyncState(id=1, last_history_id=str(new_history_id))
                db.add(sync)
            else:
                sync.last_history_id = str(new_history_id)
                sync.last_synced_at = datetime.utcnow()

        await db.commit()
        return count
