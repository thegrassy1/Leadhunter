"""BizBuySell listing scraper (WI / IL)."""

from __future__ import annotations

import re
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from scrapers.base import BaseScraper


class BizBuySellScraper(BaseScraper):
    SOURCE_NAME = "bizbuysell"
    BASE_URLS = [
        "https://www.bizbuysell.com/wisconsin-businesses-for-sale/",
        "https://www.bizbuysell.com/illinois-businesses-for-sale/",
    ]
    RATE_LIMIT_SECONDS = 4.0
    MAX_PAGES = 15

    async def scrape_listings(self) -> list[dict]:
        results: list[dict] = []
        seen: set[str] = set()
        for base in self.BASE_URLS:
            page = 1
            while page <= self.MAX_PAGES:
                url = base if page == 1 else urljoin(base, f"{page}/")
                try:
                    html = await self.fetch_html(url)
                except Exception:
                    break
                chunk = self.parse_listing(html, url)
                if not chunk:
                    break
                new_urls = False
                for row in chunk:
                    su = row.get("source_url")
                    if su and su not in seen:
                        seen.add(su)
                        results.append(row)
                        new_urls = True
                if not new_urls:
                    break
                page += 1
        # Optional: fetch first N detail pages for richer data
        enriched: list[dict] = []
        for raw in results[:80]:
            u = raw.get("source_url")
            if not u:
                enriched.append(raw)
                continue
            try:
                detail = await self.scrape_detail(u)
                merged = {**raw, **{k: v for k, v in detail.items() if v}}
                enriched.append(self.normalize(merged))
            except Exception:
                enriched.append(self.normalize(raw))
        return enriched if enriched else [self.normalize(r) for r in results]

    async def scrape_detail(self, url: str) -> dict:
        html = await self.fetch_html(url)
        soup = BeautifulSoup(html, "lxml")
        desc_el = soup.select_one("[class*='description'], .listing-description, #description")
        description = desc_el.get_text(" ", strip=True) if desc_el else None
        # Try common price / cash flow labels
        text = soup.get_text(" ", strip=True)
        asking = self.parse_money(self._label_value(soup, text, "Asking Price"))
        revenue = self.parse_money(self._label_value(soup, text, "Gross Revenue"))
        if revenue is None:
            revenue = self.parse_money(self._label_value(soup, text, "Revenue"))
        cash = self.parse_money(self._label_value(soup, text, "Cash Flow"))
        if cash is None:
            cash = self.parse_money(self._label_value(soup, text, "SDE"))
        return {
            "description": description,
            "asking_price": asking,
            "annual_revenue": revenue,
            "cash_flow": cash,
            "raw_html_snippet": html[:12000],
        }

    def _label_value(self, soup: BeautifulSoup, full_text: str, label: str) -> str | None:
        for el in soup.find_all(string=re.compile(re.escape(label), re.I)):
            if hasattr(el, "parent"):
                p = el.parent
                sib = p.find_next_sibling()
                if sib:
                    s = sib.get_text(" ", strip=True)
                    if s:
                        return s
        m = re.search(rf"{re.escape(label)}\s*[:\s]+\s*([^\n]+)", full_text, re.I)
        return m.group(1).strip() if m else None

    def parse_listing(self, html: str, page_url: str) -> list[dict]:
        soup = BeautifulSoup(html, "lxml")
        rows: list[dict] = []
        seen: set[str] = set()
        for a in soup.select("a[href]"):
            href = a.get("href") or ""
            if "/business-opportunity/" not in href and "/business-for-sale/" not in href:
                continue
            full = urljoin(page_url, href)
            if full in seen:
                continue
            seen.add(full)
            parsed = urlparse(full)
            if parsed.netloc and "bizbuysell" not in parsed.netloc:
                continue
            title = a.get_text(" ", strip=True) or None
            card = a.find_parent(["article", "div", "li"])
            loc = None
            price = None
            if card:
                t = card.get_text(" ", strip=True)
                m = re.search(
                    r"\$[\d,]+(?:\.\d+)?|\b(?:Ask|Asking)\b[^$]*\$[\d,]+",
                    t,
                    re.I,
                )
                if m:
                    price = self.parse_money(m.group(0))
                for part in t.split("•"):
                    part = part.strip()
                    if re.search(r",\s*[A-Z]{2}\b", part):
                        loc = part
                        break
            state = "WI" if "wisconsin" in page_url.lower() else "IL"
            if loc:
                m2 = re.search(r",\s*([A-Z]{2})\b", loc)
                if m2:
                    state = m2.group(1)
            city = None
            if loc:
                city = loc.split(",")[0].strip() if "," in loc else None
            rows.append(
                {
                    "source_url": full,
                    "listing_id": parsed.path.strip("/").split("/")[-1] or None,
                    "business_name": title,
                    "asking_price": price,
                    "city": city,
                    "state": state,
                    "description": None,
                    "raw_html_snippet": (card.get_text(" ", strip=True)[:4000] if card else None),
                }
            )
        return rows
