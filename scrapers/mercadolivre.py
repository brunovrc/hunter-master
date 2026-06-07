import logging
from datetime import datetime, timedelta

import httpx

from config.search_terms import BASKETBALL, FOOTBALL_BR, NEGATIVE_TITLE_TERMS, get_price_floor
from config.settings import settings

from .base import BaseScraper

logger = logging.getLogger(__name__)

ML_TOKEN_URL = "https://api.mercadolibre.com/oauth/token"
ML_SEARCH_URL = "https://api.mercadolibre.com/sites/MLB/search"


class MercadoLivreScraper(BaseScraper):
    name = "mercadolivre"

    _token: str = ""
    _token_expires: datetime = datetime.min

    async def _get_token(self, client: httpx.AsyncClient) -> str:
        if self._token and datetime.utcnow() < self._token_expires:
            return self._token

        if not settings.ml_client_id or not settings.ml_client_secret:
            logger.warning("[ML API] ML_CLIENT_ID ou ML_CLIENT_SECRET não configurados")
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
            logger.info("[ML API] Token OAuth obtido com sucesso")
        except Exception as e:
            logger.error(f"[ML API] Falha ao obter token: {e}")
            self._token = ""

        return self._token

    async def scrape(self) -> list:
        listings = []
        queries = FOOTBALL_BR + BASKETBALL

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
                        # Token expirou — renova e tenta de novo
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
                        logger.warning(f"[ML API] '{query}': HTTP {resp.status_code}")
                        continue

                    results = resp.json().get("results", [])
                    logger.info(f"[ML API] '{query}': {len(results)} items")

                    for item in results:
                        parsed = self._parse_item(item)
                        if parsed:
                            listings.append(parsed)

                except Exception as e:
                    logger.warning(f"[ML API] '{query}' erro: {e}")

        return listings

    def _parse_item(self, item: dict) -> dict | None:
        try:
            title = item.get("title", "")
            if not title:
                return None

            title_lower = title.lower()
            if any(neg in title_lower for neg in NEGATIVE_TITLE_TERMS):
                return None

            price = float(item.get("price") or 0)
            if price <= 0:
                return None

            floor = get_price_floor({"title": title, "price": price})
            if price < floor:
                return None

            item_id = str(item.get("id", ""))
            url = item.get("permalink", "")

            thumbnail = item.get("thumbnail", "")
            # Upgrade para imagem maior (D = detalhe, I = lista)
            if thumbnail:
                thumbnail = thumbnail.replace("-I.", "-O.").replace("/I/", "/O/")

            seller = item.get("seller", {})

            return self._normalize({
                "id": item_id,
                "title": title,
                "description": "",
                "price": price,
                "url": url,
                "images": [thumbnail] if thumbnail else [],
                "seller_id": str(seller.get("id", "")),
                "seller_name": seller.get("nickname", ""),
                "seller_ratings": 0,
                "seller_positive_pct": 100,
            })
        except Exception:
            return None
