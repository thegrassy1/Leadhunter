"""Lead scoring engine (0-100)."""

from __future__ import annotations

import json
from typing import Any

from models import Lead

TARGET_INDUSTRIES = [
    "service",
    "professional",
    "consulting",
    "manufacturing",
    "it",
    "technology",
    "fitness",
    "accounting",
    "ecommerce",
    "retail",
    "transportation",
    "healthcare",
    "home health",
    "med spa",
    "medical",
]

MOTIVATION_KEYWORDS = [
    "retire",
    "retiring",
    "retirement",
    "health",
    "relocat",
    "moving",
    "divorce",
    "must sell",
    "motivated",
    "price reduced",
    "quick sale",
    "owner financing",
    "turnkey",
    "ready to transition",
]

EXCLUDE_KEYWORDS = [
    "franchise",
    "mlm",
    "multi-level",
    "cannabis",
    "hemp",
    "marijuana",
    "adult",
    "gentlemen",
    "vape",
]

# Southern / central WI — city prefixes and ZIP ranges (approximate)
WI_TARGET_CITIES = frozenset(
    {
        "madison",
        "milwaukee",
        "janesville",
        "racine",
        "kenosha",
        "waukesha",
        "green bay",
        "appleton",
        "oshkosh",
        "fond du lac",
        "sheboygan",
        "west allis",
        "wauwatosa",
        "brookfield",
        "eau claire",
        "la crosse",
        "beloit",
        "oshkosh",
        "stevens point",
        "wisconsin dells",
    }
)

# Northern IL — north of I-80 corridor (rough city list)
IL_TARGET_CITIES = frozenset(
    {
        "rockford",
        "dekalb",
        "elgin",
        "waukegan",
        "aurora",
        "joliet",
        "naperville",
        "schaumburg",
        "arlington heights",
        "evanston",
        "skokie",
        "des plaines",
        "palatine",
        "wheeling",
        "mundelein",
        "vernon hills",
        "gurnee",
        "mchenry",
        "crystal lake",
        "algonquin",
        "cary",
        "lake forest",
        "highland park",
        "northbrook",
    }
)


def _zip_int(pc: str | None) -> int | None:
    if not pc:
        return None
    digits = "".join(c for c in pc if c.isdigit())[:5]
    if len(digits) < 5:
        return None
    return int(digits)


def is_target_wi_area(city: str | None, postal_code: str | None) -> bool:
    if city:
        c = city.lower().strip()
        for t in WI_TARGET_CITIES:
            if t in c or c.startswith(t):
                return True
    z = _zip_int(postal_code)
    if z is not None:
        # WI ZIPs 530xx-549xx; focus southern/central bands (rough)
        if 53000 <= z <= 54999:
            if z < 54500 or (53800 <= z <= 54999):
                return True
    return False


def is_target_il_area(city: str | None, postal_code: str | None) -> bool:
    if city:
        c = city.lower().strip()
        for t in IL_TARGET_CITIES:
            if t in c or c.startswith(t):
                return True
    z = _zip_int(postal_code)
    if z is not None:
        # Northern IL ZIPs often 600xx-611xx (exclude far south 609+ near border carefully)
        if 60000 <= z <= 61199:
            return True
    return False


def score_lead(lead: Lead) -> tuple[int, dict[str, int]]:
    breakdown: dict[str, int] = {}

    if lead.state == "WI" and is_target_wi_area(lead.city, lead.postal_code):
        breakdown["geography"] = 25
    elif lead.state == "IL" and is_target_il_area(lead.city, lead.postal_code):
        breakdown["geography"] = 25
    elif lead.state in ("WI", "IL"):
        breakdown["geography"] = 10
    else:
        breakdown["geography"] = 0

    if lead.annual_revenue:
        if 1_000_000 <= lead.annual_revenue <= 15_000_000:
            breakdown["revenue_range"] = 20
        elif 500_000 <= lead.annual_revenue < 1_000_000:
            breakdown["revenue_range"] = 10
        else:
            breakdown["revenue_range"] = 0
    else:
        breakdown["revenue_range"] = 5

    ind = (lead.industry or "").lower()
    if any(t in ind for t in TARGET_INDUSTRIES):
        breakdown["industry_fit"] = 15
    elif lead.industry:
        breakdown["industry_fit"] = 5
    else:
        breakdown["industry_fit"] = 7

    if lead.employee_count and lead.employee_count >= 5:
        breakdown["employee_count"] = 10
    elif lead.employee_count and lead.employee_count >= 2:
        breakdown["employee_count"] = 5
    else:
        breakdown["employee_count"] = 3

    desc = (lead.description or "").lower()
    matches = sum(1 for kw in MOTIVATION_KEYWORDS if kw in desc)
    breakdown["motivation_signals"] = min(matches * 3, 10)

    rt = (lead.revenue_trend or "unknown").lower()
    if rt == "increasing":
        breakdown["revenue_trend"] = 10
    elif rt == "steady":
        breakdown["revenue_trend"] = 8
    elif rt == "unknown":
        breakdown["revenue_trend"] = 4
    else:
        breakdown["revenue_trend"] = 0

    if any(kw in desc for kw in EXCLUDE_KEYWORDS) or lead.is_franchise:
        breakdown["not_excluded"] = 0
    else:
        breakdown["not_excluded"] = 10

    total = min(100, sum(breakdown.values()))
    return total, breakdown


def apply_score_to_lead(lead: Lead) -> None:
    total, breakdown = score_lead(lead)
    lead.lead_score = total
    lead.score_breakdown = json.dumps(breakdown)


def breakdown_dict_from_str(s: str | None) -> dict[str, Any]:
    if not s:
        return {}
    try:
        return dict(json.loads(s))
    except Exception:
        return {}
