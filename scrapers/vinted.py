"""
Vinted scraper — usa API interna (sem Playwright).
Monitora FR, UK e ES para camisas autografadas de jogadores brasileiros/internacionais.
"""
import logging

import httpx

from config.search_terms import NEGATIVE_TITLE_TERMS, get_price_floor

from .base import BaseScraper

logger = logging.getLogger(__name__)

# Taxa de câmbio → BRL (jun/2026)
CURRENCY_TO_BRL = {
    "EUR": 5.50,
    "GBP": 6.80,
}

# Domínios monitorados: (base_url, moeda)
VINTED_DOMAINS = [
    ("https://www.vinted.fr",    "EUR"),
    ("https://www.vinted.co.uk", "GBP"),
    ("https://www.vinted.es",    "EUR"),
]

SEARCH_TERMS = [
    # Genérico
    "signed jersey",
    "autographed jersey",
    "match worn jersey",
    "signed shirt football",
    # Francês
    "maillot signé",
    "maillot dédicacé",
    "maillot match worn",
    # Espanhol
    "camiseta firmada",
    "camiseta autografiada futbol",
    # Jogadores específicos
    "Neymar signed",
    "Ronaldinho signed",
    "Pelé signed",
    "Messi signed jersey",
    "Ronaldo signed jersey",
    "Vinicius signed",
    "Mbappé signed jersey",
]

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9,fr;q=0.8",
}


class VintedScraper(BaseScraper):
    name = "vinted"

    async def scrape(self) -> list:
        listings = []

        async with httpx.AsyncClient(
            timeout=20, headers=_HEADERS, follow_redirects=True
        ) as client:
            for base_url, currency in VINTED_DOMAINS:
                # Obter cookies de sessão primeiro
                try:
                    await client.get(base_url)
                except Exception:
                    pass

                rate = CURRENCY_TO_BRL[currency]

                for term in SEARCH_TERMS:
                    try:
                        resp = await client.get(
                            f"{base_url}/api/v2/catalog/items",
                            params={
                                "search_text": term,
                                "per_page": 96,
                                "order": "newest_first",
                            },
                        )

                        if resp.status_code != 200:
                            logger.warning(
                                f"[Vinted] '{term}' @ {base_url}: HTTP {resp.status_code}"
                            )
                            continue

                        items = resp.json().get("items", [])
                        logger.info(f"[Vinted] '{term}' @ {base_url}: {len(items)} items")

                        for item in items:
                            parsed = self._parse_item(item, rate, base_url)
                            if parsed:
                                listings.append(parsed)

                    except Exception as e:
                        logger.warning(f"[Vinted] '{term}' @ {base_url}: {e}")

        return listings

    def _parse_item(self, item: dict, rate: float, base_url: str) -> dict | None:
        try:
            title = item.get("title", "")
            if not title:
                return None

            title_lower = title.lower()
            if any(neg in title_lower for neg in NEGATIVE_TITLE_TERMS):
                return None

            # price pode ser string "45.00" ou dict {"amount": "45.00"}
            raw_price = item.get("price", 0)
            if isinstance(raw_price, dict):
                raw_price = raw_price.get("amount", 0)
            try:
                price_local = float(str(raw_price).replace(",", "."))
            except (ValueError, TypeError):
                return None

            if price_local <= 0:
                return None

            price_brl = price_local * rate
            floor = get_price_floor({"title": title, "price": price_brl})
            if price_brl < floor:
                return None

            item_id = str(item.get("id", ""))
            url = item.get("url", "")
            if url and not url.startswith("http"):
                url = base_url + url

            photos = item.get("photos", [])
            img = ""
            if photos:
                photo = photos[0]
                img = photo.get("full_size_url") or photo.get("url", "")

            user = item.get("user", {})
            feedback = float(user.get("feedback_reputation") or 1.0)

            return self._normalize({
                "id": item_id,
                "title": title,
                "description": item.get("description", ""),
                "price": price_brl,
                "url": url,
                "images": [img] if img else [],
                "seller_id": str(user.get("id", "")),
                "seller_name": user.get("login", ""),
                "seller_ratings": 0,
                "seller_positive_pct": feedback * 100,
            })
        except Exception:
            return None
