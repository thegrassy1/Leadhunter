"""Base scraper: robots.txt, rate limit, retries, parsing hooks."""

from __future__ import annotations

import asyncio
import random
import re
import time
from abc import ABC, abstractmethod
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

import httpx
from bs4 import BeautifulSoup


class BaseScraper(ABC):
    """All scrapers implement this interface."""

    SOURCE_NAME: str
    BASE_URLS: list[str]
    RATE_LIMIT_SECONDS: float = 4.0
    USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 LeadHunter/1.0"
    )
    MAX_RETRIES = 3

    def __init__(self) -> None:
        self._last_request_at: float = 0.0
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                headers={"User-Agent": self.USER_AGENT},
                follow_redirects=True,
                timeout=httpx.Timeout(45.0),
            )
        return self._client

    async def aclose(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def _rate_limit(self) -> None:
        base = getattr(self, "RATE_LIMIT_SECONDS", 4.0)
        jitter = random.uniform(0.5, 1.5)
        delay = max(3.0, base + jitter)
        elapsed = time.monotonic() - self._last_request_at
        if elapsed < delay:
            await asyncio.sleep(delay - elapsed)

    async def allowed_to_fetch(self, url: str) -> bool:
        """Fetch robots.txt with httpx, then parse with RobotFileParser."""

        parsed = urlparse(url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        client = await self._get_client()
        try:
            r = await client.get(robots_url)
            if r.status_code != 200:
                return True
            text = r.text
        except Exception:
            return True

        def _check() -> bool:
            rp = RobotFileParser()
            rp.set_url(robots_url)
            try:
                rp.parse(text.splitlines())
            except Exception:
                return True
            try:
                return rp.can_fetch(self.USER_AGENT, url) or rp.can_fetch("*", url)
            except Exception:
                return True

        return await asyncio.to_thread(_check)

    async def fetch_html(self, url: str) -> str:
        if not await self.allowed_to_fetch(url):
            raise PermissionError(f"robots.txt disallows fetching: {url}")
        await self._rate_limit()
        client = await self._get_client()
        last_exc: Exception | None = None
        for attempt in range(self.MAX_RETRIES):
            try:
                r = await client.get(url)
                self._last_request_at = time.monotonic()
                r.raise_for_status()
                return r.text
            except Exception as e:
                last_exc = e
                await asyncio.sleep(2**attempt + random.uniform(0, 1))
        raise last_exc or RuntimeError("fetch failed")

    @abstractmethod
    async def scrape_listings(self) -> list[dict]:
        """Scrape listing index pages, return raw lead dicts."""

    async def scrape_detail(self, url: str) -> dict:
        """Optional detail page — default returns empty dict."""
        return {}

    @abstractmethod
    def parse_listing(self, html: str, page_url: str) -> list[dict]:
        """Parse a listing/list page HTML into partial lead dicts."""

    def normalize(self, raw: dict) -> dict:
        """Normalize keys for DB upsert."""
        out = dict(raw)
        out.setdefault("source", self.SOURCE_NAME)
        if out.get("state"):
            out["state"] = str(out["state"])[:2].upper()
        return out

    @staticmethod
    def parse_money(text: str | None) -> float | None:
        if not text:
            return None
        t = re.sub(r"[^\d.]", "", text.replace(",", ""))
        if not t:
            return None
        try:
            return float(t)
        except ValueError:
            return None
