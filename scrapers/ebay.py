"""
eBay scraper — monitora vendedores específicos via Finding API.
Requer EBAY_APP_ID no .env (grátis em developer.ebay.com).
"""
import logging

import httpx

from config.search_terms import NEGATIVE_TITLE_TERMS, get_price_floor
from config.settings import settings

from .base import BaseScraper

logger = logging.getLogger(__name__)

FINDING_API = "https://svcs.ebay.com/services/search/FindingService/v1"

# USD → BRL (jun/2026)
USD_TO_BRL = 5.75

# ── Lojas monitoradas ─────────────────────────────────────────────────────────
# Nome exato da loja como aparece no eBay (nome de exibição).
MONITORED_STORES = [
    "sportsnstuff408",
    "RJ Duke Sports",
    "Certified Authentic Collectibles",
]

SEARCH_KEYWORDS = [
    "signed jersey",
    "autographed jersey",
    "match worn jersey",
    "signed shirt",
    "autographed basketball jersey",
]


class EbayScraper(BaseScraper):
    name = "ebay"

    async def scrape(self) -> list:
        if not settings.ebay_app_id:
            logger.warning("[eBay] EBAY_APP_ID não configurado — adicione ao .env")
            return []

        listings = []

        async with httpx.AsyncClient(timeout=20) as client:
            for store in MONITORED_STORES:
                for keyword in SEARCH_KEYWORDS:
                    try:
                        params = [
                            ("OPERATION-NAME", "findItemsIneBayStores"),
                            ("SERVICE-VERSION", "1.0.0"),
                            ("SECURITY-APPNAME", settings.ebay_app_id),
                            ("RESPONSE-DATA-FORMAT", "JSON"),
                            ("storeName", store),
                            ("keywords", keyword),
                            ("paginationInput.entriesPerPage", "100"),
                            ("sortOrder", "StartTimeNewest"),
                            ("outputSelector(0)", "SellerInfo"),
                            ("outputSelector(1)", "PictureURLLarge"),
                        ]

                        resp = await client.get(FINDING_API, params=params)
                        if resp.status_code != 200:
                            logger.warning(f"[eBay] '{store}'/'{keyword}': HTTP {resp.status_code}")
                            continue

                        data = resp.json()
                        results = (
                            data.get("findItemsIneBayStoresResponse", [{}])[0]
                            .get("searchResult", [{}])[0]
                            .get("item", [])
                        )
                        logger.info(f"[eBay] '{store}' / '{keyword}': {len(results)} items")

                        for item in results:
                            parsed = self._parse_item(item)
                            if parsed:
                                listings.append(parsed)

                    except Exception as e:
                        logger.warning(f"[eBay] '{store}'/'{keyword}' erro: {e}")

        return listings

    def _parse_item(self, item: dict) -> dict | None:
        try:
            title = (item.get("title") or [""])[0]
            if not title:
                return None

            title_lower = title.lower()
            if any(neg in title_lower for neg in NEGATIVE_TITLE_TERMS):
                return None

            price_usd = float(
                (item.get("sellingStatus") or [{}])[0]
                .get("currentPrice", [{"__value__": "0"}])[0]
                .get("__value__", 0)
            )
            if price_usd <= 0:
                return None

            price_brl = price_usd * USD_TO_BRL
            floor = get_price_floor({"title": title, "price": price_brl})
            if price_brl < floor:
                return None

            item_id = (item.get("itemId") or [""])[0]
            url = (item.get("viewItemURL") or [""])[0]

            large = (item.get("pictureURLLarge") or [""])[0]
            thumb = (item.get("galleryURL") or [""])[0]
            img = large or thumb

            seller_info = (item.get("sellerInfo") or [{}])[0]
            seller_name = (seller_info.get("sellerUserName") or [""])[0]
            feedback_score = int((seller_info.get("feedbackScore") or ["0"])[0] or 0)
            feedback_pct = float((seller_info.get("positiveFeedbackPercent") or ["100"])[0] or 100)

            return self._normalize({
                "id": item_id,
                "title": title,
                "description": "",
                "price": price_brl,
                "url": url,
                "images": [img] if img else [],
                "seller_id": seller_name,
                "seller_name": seller_name,
                "seller_ratings": feedback_score,
                "seller_positive_pct": feedback_pct,
            })
        except Exception:
            return None
