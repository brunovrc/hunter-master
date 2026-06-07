import logging
from datetime import datetime, timedelta

import httpx

from config.search_terms import BASKETBALL, FOOTBALL_AR, NEGATIVE_TITLE_TERMS, get_price_floor
from config.settings import settings

from .base import BaseScraper

logger = logging.getLogger(__name__)

ML_TOKEN_URL = "https://api.mercadolibre.com/oauth/token"
ML_SEARCH_URL = "https://api.mercadolibre.com/sites/MLA/search"

# 1 BRL ≈ 6 ARS (jun/2026) — ajustar conforme mercado
ARS_TO_BRL = 1 / 6.0


class MercadoLivreArgentinaScraper(BaseScraper):
    name = "mercadolivre_ar"

    _token: str = ""
    _token_expires: datetime = datetime.min

    async def _get_token(self, client: httpx.AsyncClient) -> str:
        if self._token and datetime.utcnow() < self._token_expires:
            return self._token

        if not settings.ml_client_id or not settings.ml_client_secret:
            return ""

        try:
            resp = await client.post(ML_TOKEN_URL, data={
                "grant_type": "client_credentials",
                "client_id": settings.ml_client_id,
                "client_secret": settings.ml_client_secret,
            }, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            self._token = data.get("access_token", "")
            expires_in = int(data.get("expires_in", 21600))
            self._token_expires = datetime.utcnow() + timedelta(seconds=expires_in - 120)
        except Exception as e:
            logger.error(f"[ML-AR API] Falha ao obter token: {e}")
            self._token = ""

        return self._token

    async def scrape(self) -> list:
        listings = []
        queries = FOOTBALL_AR + BASKETBALL

        async with httpx.AsyncClient(timeout=20) as client:
            token = await self._get_token(client)
            if not token:
                return []

            headers = {"Authorization": f"Bearer {token}"}

            for query in queries:
                if any(neg in query.lower() for neg in NEGATIVE_TITLE_TERMS):
                    continue

                try:
                    resp = await client.get(
                        ML_SEARCH_URL,
                        headers=headers,
                        params={"q": query, "limit": 50},
                    )
                    if resp.status_code == 401:
                        self._token = ""
                        token = await self._get_token(client)
                        if not token:
                            break
                        headers = {"Authorization": f"Bearer {token}"}
                        resp = await client.get(
                            ML_SEARCH_URL,
                            headers=headers,
                            params={"q": query, "limit": 50},
                        )

                    if resp.status_code != 200:
                        logger.warning(f"[ML-AR API] '{query}': HTTP {resp.status_code}")
                        continue

                    results = resp.json().get("results", [])
                    logger.info(f"[ML-AR API] '{query}': {len(results)} items")

                    for item in results:
                        parsed = self._parse_item(item)
                        if parsed:
                            listings.append(parsed)

                except Exception as e:
                    logger.warning(f"[ML-AR API] '{query}' erro: {e}")

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
