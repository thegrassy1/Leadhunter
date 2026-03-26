"""Optional Apollo.io / public enrichment (stub)."""

from __future__ import annotations

from models import Lead


async def enrich_lead(_lead: Lead) -> dict:
    """Placeholder for future enrichment."""
    return {}
