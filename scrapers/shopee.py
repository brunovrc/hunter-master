import asyncio
import logging

import httpx

from .base import BaseScraper

logger = logging.getLogger(__name__)

SHOPEE_SEARCHES = [
    "camisa futebol autografada",
    "camisa futebol assinada jogador",
    "camisa futebol match worn",
    "camisa futebol usada em jogo",
    "pelé autografado camisa",
    "zico autografado camisa",
    "neymar autografado camisa",
    "camisa nba autografada",
    "camisa basquete autografada",
    "jordan camisa autografada",
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Referer": "https://shopee.com.br/",
    "If-None-Match-": "",
    "X-API-SOURCE": "pc",
    "X-Requested-With": "XMLHttpRequest",
}


class ShopeeScraper(BaseScraper):
    name = "shopee"

    async def scrape(self) -> list:
        listings = []

        async with httpx.AsyncClient(headers=HEADERS, timeout=30, follow_redirects=True) as client:
            for query in SHOPEE_SEARCHES:
                try:
                    items = await self._search(client, query)
                    for item in items:
                        parsed = self._parse(item, query)
                        if parsed:
                            listings.append(parsed)
                    await asyncio.sleep(2)
                except Exception as e:
                    logger.warning(f"[Shopee] '{query}' falhou: {e}")

        return listings

    async def _search(self, client: httpx.AsyncClient, query: str) -> list:
        params = {
            "by": "ctime",
            "keyword": query,
            "limit": 20,
            "newest": 0,
            "order": "desc",
            "page_type": "search",
            "scenario": "PAGE_GLOBAL_SEARCH",
            "version": 2,
        }
        resp = await client.get(
            "https://shopee.com.br/api/v4/search/search_items",
            params=params,
        )
        if resp.status_code != 200:
            logger.debug(f"[Shopee] HTTP {resp.status_code} para '{query}'")
            return []

        data = resp.json()
        items = data.get("items", []) or []
        logger.info(f"[Shopee] '{query}': {len(items)} resultados")
        return items

    def _parse(self, item: dict, query: str) -> dict | None:
        try:
            info = item.get("item_basic", item)

            title = info.get("name", "")
            if not title:
                return None

            # Preço vem em centavos
            price_raw = info.get("price", 0) or info.get("price_min", 0)
            price = price_raw / 100_000  # Shopee usa preço * 100000

            if price < 100:
                return None

            item_id = str(info.get("itemid", ""))
            shop_id = str(info.get("shopid", ""))
            url = f"https://shopee.com.br/product/{shop_id}/{item_id}" if item_id else ""

            images = info.get("images", []) or []
            img_urls = [
                f"https://cf.shopee.com.br/file/{img}"
                for img in images[:3]
                if img
            ]

            if not img_urls:
                thumb = info.get("image", "")
                if thumb:
                    img_urls = [f"https://cf.shopee.com.br/file/{thumb}"]

            seller_rating = info.get("item_rating", {}).get("rating_star", 0) or 0

            return self._normalize({
                "id": f"shopee_{item_id}",
                "title": title,
                "description": info.get("description", "")[:500],
                "price": price,
                "url": url,
                "images": img_urls,
                "seller_ratings": int(info.get("sold", 0) or 0),
                "seller_positive_pct": min(100, int(seller_rating * 20)),
            })
        except Exception:
            return None
