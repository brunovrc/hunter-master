"""
MercadoLibre Argentina scraper — API pública, sem OAuth.
"""
import logging

import httpx

from config.search_terms import BASKETBALL, FOOTBALL_AR, NEGATIVE_TITLE_TERMS, get_price_floor

from .base import BaseScraper

logger = logging.getLogger(__name__)

ML_AR_SEARCH_URL = "https://api.mercadolibre.com/sites/MLA/search"

# ARS → BRL (jun/2026)
ARS_TO_BRL = 1 / 6.0

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; HunterMaster/1.0)",
    "Accept": "application/json",
}


class MercadoLivreArgentinaScraper(BaseScraper):
    name = "mercadolivre_ar"

    async def scrape(self) -> list:
        listings = []
        queries = FOOTBALL_AR + BASKETBALL

        async with httpx.AsyncClient(timeout=20, headers=_HEADERS) as client:
            for query in queries:
                if any(neg in query.lower() for neg in NEGATIVE_TITLE_TERMS):
                    continue

                try:
                    resp = await client.get(
                        ML_AR_SEARCH_URL,
                        params={"q": query, "limit": 50},
                    )

                    if resp.status_code != 200:
                        logger.warning(f"[ML-AR] '{query}': HTTP {resp.status_code}")
                        continue

                    results = resp.json().get("results", [])
                    logger.info(f"[ML-AR] '{query}': {len(results)} items")

                    for item in results:
                        parsed = self._parse_item(item)
                        if parsed:
                            listings.append(parsed)

                except Exception as e:
                    logger.warning(f"[ML-AR] '{query}' erro: {e}")

        return listings

    def _parse_item(self, item: dict) -> dict | None:
        try:
            title = item.get("title", "")
            if not title:
                return None

            title_lower = title.lower()
            if any(neg in title_lower for neg in NEGATIVE_TITLE_TERMS):
                return None

            price_ars = float(item.get("price") or 0)
            if price_ars <= 0:
                return None

            price_brl = price_ars * ARS_TO_BRL
            floor = get_price_floor({"title": title, "price": price_brl})
            if price_brl < floor:
                return None

            item_id = str(item.get("id", ""))
            url = item.get("permalink", "")

            thumbnail = item.get("thumbnail", "")
            if thumbnail:
                thumbnail = thumbnail.replace("-I.", "-O.").replace("/I/", "/O/")

            seller = item.get("seller", {})

            return self._normalize({
                "id": item_id,
                "title": title,
                "description": "",
                "price": price_brl,
                "url": url,
                "images": [thumbnail] if thumbnail else [],
                "seller_id": str(seller.get("id", "")),
                "seller_name": seller.get("nickname", ""),
                "seller_ratings": 0,
                "seller_positive_pct": 100,
            })
        except Exception:
            return None
