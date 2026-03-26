from scrapers.base import BaseScraper
from scrapers.bizbuysell import BizBuySellScraper
from scrapers.bizquest import BizQuestScraper
from scrapers.businessbroker import BusinessBrokerScraper

SCRAPER_REGISTRY: dict[str, type[BaseScraper]] = {
    "bizbuysell": BizBuySellScraper,
    "bizquest": BizQuestScraper,
    "businessbroker": BusinessBrokerScraper,
}


def get_scraper(source: str) -> BaseScraper:
    cls = SCRAPER_REGISTRY.get(source.lower())
    if not cls:
        raise ValueError(f"Unknown scraper source: {source}")
    return cls()
