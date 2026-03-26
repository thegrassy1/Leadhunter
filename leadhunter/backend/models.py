"""SQLAlchemy ORM models."""

from datetime import datetime
from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source: Mapped[str] = mapped_column(String(64), nullable=False)
    source_url: Mapped[str | None] = mapped_column(String(2048), unique=True, nullable=True)
    listing_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    raw_html_snippet: Mapped[str | None] = mapped_column(Text, nullable=True)

    business_name: Mapped[str | None] = mapped_column(String(512), nullable=True)
    industry: Mapped[str | None] = mapped_column(String(256), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    address: Mapped[str | None] = mapped_column(String(512), nullable=True)
    city: Mapped[str | None] = mapped_column(String(128), nullable=True)
    state: Mapped[str | None] = mapped_column(String(8), nullable=True)
    postal_code: Mapped[str | None] = mapped_column(String(32), nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)

    asking_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    annual_revenue: Mapped[float | None] = mapped_column(Float, nullable=True)
    cash_flow: Mapped[float | None] = mapped_column(Float, nullable=True)
    revenue_trend: Mapped[str | None] = mapped_column(String(32), nullable=True)

    owner_name: Mapped[str | None] = mapped_column(String(256), nullable=True)
    owner_email: Mapped[str | None] = mapped_column(String(256), nullable=True)
    owner_phone: Mapped[str | None] = mapped_column(String(64), nullable=True)

    employee_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    years_established: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_franchise: Mapped[bool] = mapped_column(Boolean, default=False, server_default="0")

    lead_score: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    score_breakdown: Mapped[str | None] = mapped_column(Text, nullable=True)

    status: Mapped[str] = mapped_column(String(32), default="new", server_default="new")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    scraped_at: Mapped[datetime | None] = mapped_column(
        server_default=func.current_timestamp(), nullable=True
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
        nullable=True,
    )
    last_contacted_at: Mapped[datetime | None] = mapped_column(nullable=True)

    email_drafts: Mapped[list["EmailDraft"]] = relationship(back_populates="lead")
    inbound_emails: Mapped[list["InboundEmail"]] = relationship(back_populates="lead")


class ScrapeRun(Base):
    __tablename__ = "scrape_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="running", server_default="running")
    leads_found: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    leads_new: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    leads_updated: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    started_at: Mapped[datetime | None] = mapped_column(
        server_default=func.current_timestamp(), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)


class EmailDraft(Base):
    __tablename__ = "email_drafts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    lead_id: Mapped[int] = mapped_column(ForeignKey("leads.id"), nullable=False)
    subject: Mapped[str | None] = mapped_column(String(512), nullable=True)
    body: Mapped[str | None] = mapped_column(Text, nullable=True)
    tone: Mapped[str] = mapped_column(String(32), default="professional", server_default="professional")
    status: Mapped[str] = mapped_column(String(32), default="draft", server_default="draft")
    gmail_message_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    gmail_thread_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    sent_at: Mapped[datetime | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(
        server_default=func.current_timestamp(), nullable=True
    )

    lead: Mapped["Lead"] = relationship(back_populates="email_drafts")


class EmailTemplate(Base):
    __tablename__ = "email_templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    subject_template: Mapped[str | None] = mapped_column(Text, nullable=True)
    body_template: Mapped[str | None] = mapped_column(Text, nullable=True)
    use_case: Mapped[str | None] = mapped_column(String(64), nullable=True)


class InboundEmail(Base):
    __tablename__ = "inbound_emails"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    lead_id: Mapped[int | None] = mapped_column(ForeignKey("leads.id"), nullable=True)
    gmail_message_id: Mapped[str | None] = mapped_column(String(128), unique=True, nullable=True)
    gmail_thread_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    from_email: Mapped[str | None] = mapped_column(String(512), nullable=True)
    from_name: Mapped[str | None] = mapped_column(String(256), nullable=True)
    subject: Mapped[str | None] = mapped_column(String(512), nullable=True)
    body_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    body_snippet: Mapped[str | None] = mapped_column(String(512), nullable=True)
    received_at: Mapped[datetime | None] = mapped_column(nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, server_default="0")
    created_at: Mapped[datetime | None] = mapped_column(
        server_default=func.current_timestamp(), nullable=True
    )

    lead: Mapped["Lead | None"] = relationship(back_populates="inbound_emails")


class GmailSyncState(Base):
    __tablename__ = "gmail_sync_state"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    last_history_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    last_synced_at: Mapped[datetime | None] = mapped_column(nullable=True)


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    type: Mapped[str] = mapped_column(String(64), nullable=False)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    lead_id: Mapped[int | None] = mapped_column(ForeignKey("leads.id"), nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, server_default="0")
    created_at: Mapped[datetime | None] = mapped_column(
        server_default=func.current_timestamp(), nullable=True
    )
