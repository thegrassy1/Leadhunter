"""Pydantic request/response schemas."""

from datetime import datetime
from typing import Any

import json

from pydantic import BaseModel, ConfigDict, Field, field_validator


class LeadBase(BaseModel):
    business_name: str | None = None
    industry: str | None = None
    description: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None
    asking_price: float | None = None
    annual_revenue: float | None = None
    cash_flow: float | None = None
    employee_count: int | None = None
    status: str | None = None
    notes: str | None = None


class LeadCreate(LeadBase):
    source: str
    source_url: str | None = None


class LeadUpdate(BaseModel):
    business_name: str | None = None
    industry: str | None = None
    description: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None
    asking_price: float | None = None
    annual_revenue: float | None = None
    cash_flow: float | None = None
    revenue_trend: str | None = None
    owner_name: str | None = None
    owner_email: str | None = None
    owner_phone: str | None = None
    employee_count: int | None = None
    years_established: int | None = None
    is_franchise: bool | None = None
    status: str | None = None
    notes: str | None = None


class LeadOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    source: str
    source_url: str | None
    listing_id: str | None
    business_name: str | None
    industry: str | None
    description: str | None
    address: str | None
    city: str | None
    state: str | None
    postal_code: str | None
    asking_price: float | None
    annual_revenue: float | None
    cash_flow: float | None
    revenue_trend: str | None
    owner_name: str | None
    owner_email: str | None
    owner_phone: str | None
    employee_count: int | None
    years_established: int | None
    is_franchise: bool
    lead_score: int
    score_breakdown: dict[str, Any] = Field(default_factory=dict)
    status: str
    notes: str | None
    scraped_at: datetime | None
    updated_at: datetime | None
    last_contacted_at: datetime | None

    @field_validator("score_breakdown", mode="before")
    @classmethod
    def _score_breakdown(cls, v: Any) -> dict[str, Any]:
        if isinstance(v, dict):
            return v
        if not v:
            return {}
        try:
            return dict(json.loads(v)) if isinstance(v, str) else {}
        except Exception:
            return {}


class PaginatedLeads(BaseModel):
    items: list[LeadOut]
    total: int
    page: int
    page_size: int


class DashboardStatsOut(BaseModel):
    total_leads: int
    avg_score: float
    new_this_week: int
    leads_by_status: dict[str, int]
    score_distribution: list[dict[str, Any]]
    leads_by_industry: list[dict[str, Any]]
    geography_wi_il: dict[str, int]
    replies_received: int
    reply_rate_pct: float


class ScrapeRunOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    source: str
    status: str
    leads_found: int
    leads_new: int
    leads_updated: int
    started_at: datetime | None
    completed_at: datetime | None
    error_message: str | None


class ScraperRunRequest(BaseModel):
    source: str = Field(..., description="bizbuysell | bizquest | businessbroker")


class ScraperScheduleRequest(BaseModel):
    source: str
    cron: str
    enabled: bool = True


class EmailDraftOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    lead_id: int
    subject: str | None
    body: str | None
    tone: str
    status: str
    gmail_message_id: str | None
    gmail_thread_id: str | None
    sent_at: datetime | None
    created_at: datetime | None


class InboundEmailOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    lead_id: int | None
    gmail_message_id: str | None
    gmail_thread_id: str | None
    from_email: str | None
    from_name: str | None
    subject: str | None
    body_text: str | None
    body_snippet: str | None
    received_at: datetime | None
    is_read: bool


class EmailTemplateOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    subject_template: str | None
    body_template: str | None
    use_case: str | None


class EmailTemplateCreate(BaseModel):
    name: str
    subject_template: str | None = None
    body_template: str | None = None
    use_case: str | None = None


class ExportRequest(BaseModel):
    filters: dict[str, Any] | None = None
