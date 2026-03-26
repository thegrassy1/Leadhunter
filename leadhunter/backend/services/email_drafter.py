"""Anthropic-powered email draft generation."""

from __future__ import annotations

import json
import re

from anthropic import AsyncAnthropic

from config import settings
from models import Lead


async def generate_email_draft(
    lead: Lead, template_type: str = "initial_outreach"
) -> dict[str, str]:
    """Generate subject + body via Claude."""
    client = AsyncAnthropic(api_key=settings.anthropic_api_key or "dummy")
    ap = lead.asking_price
    price_s = f"${ap:,.0f}" if ap else "Not listed"
    desc = (lead.description or "")[:500] if lead.description else "N/A"
    prompt = f"""You are writing a business acquisition outreach email.
The sender is interested in acquiring small businesses in Wisconsin/Illinois.

Write a {template_type} email to the business owner.

Business details:
- Business: {lead.business_name}
- Industry: {lead.industry}
- Location: {lead.city}, {lead.state}
- Listed on: {lead.source}
- Description: {desc}
- Asking price: {price_s}

Requirements:
- Professional but warm tone
- Brief (under 150 words)
- Reference something specific about their business
- Don't be pushy — express interest in learning more
- Include a soft call to action (phone call or coffee meeting)
- Do NOT mention scraping or automated tools

Return ONLY valid JSON with keys "subject" and "body" (strings). No markdown."""

    if not settings.anthropic_api_key:
        return {
            "subject": f"Inquiry regarding {lead.business_name or 'your business'}",
            "body": (
                f"Hello,\n\nI came across your listing and wanted to reach out "
                f"regarding {lead.business_name or 'your company'} in {lead.city}, {lead.state}. "
                f"I would welcome a brief conversation at your convenience.\n\n"
                f"Best regards"
            ),
        }

    msg = await client.messages.create(
        model=settings.anthropic_model,
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}],
    )
    text = ""
    for block in msg.content:
        if hasattr(block, "text"):
            text += block.text
    return parse_json_response(text)


def parse_json_response(text: str) -> dict[str, str]:
    text = text.strip()
    m = re.search(r"\{[\s\S]*\}", text)
    if m:
        text = m.group(0)
    try:
        data = json.loads(text)
        return {
            "subject": str(data.get("subject", "Follow up")),
            "body": str(data.get("body", "")),
        }
    except Exception:
        return {"subject": "Business inquiry", "body": text}
