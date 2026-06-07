import logging

from playwright.async_api import async_playwright

from config.search_terms import ENJOEI_BR, NEGATIVE_TITLE_TERMS, get_price_floor
from .anti_detection import get_browser_context, human_delay, safe_text, safe_attr
from .base import BaseScraper

logger = logging.getLogger(__name__)

BASE_URL = "https://www.enjoei.com.br/s?q={}&sort=recent"

_MAX_CARDS = 20


class EnjoeiScraper(BaseScraper):
    name = "enjoei"

    async def scrape(self) -> list:
        listings = []

        async with async_playwright() as p:
            browser, context = await get_browser_context(p, locale="pt-BR")
            try:
                page = await context.new_page()

                for query in ENJOEI_BR:
                    url = BASE_URL.format(query.replace(" ", "+"))
                    try:
                        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
                        await human_delay(2.5, 5.0)

                        cards = await page.query_selector_all("div.c-product-card")
                        logger.info(f"[Enjoei] '{query}': {len(cards)} cards (limitando a {_MAX_CARDS})")

                        for card in cards[:_MAX_CARDS]:
                            parsed = await self._parse_card(card)
                            if parsed:
                                listings.append(parsed)

                        await human_delay(1.5, 3.0)
                    except Exception as e:
                        logger.warning(f"[Enjoei] '{query}' falhou: {e}")
            finally:
                await browser.close()

        return listings

    async def _parse_card(self, card) -> dict | None:
        try:
            title = await safe_text(card, [
                "h2[data-test='div-nome-prod']",
                "h3[data-test='div-nome-prod']",
                "[class*='product-name']",
                "[class*='title']",
            ])
            if not title:
                return None

            title_lower = title.lower()
            if any(neg in title_lower for neg in NEGATIVE_TITLE_TERMS):
                return None

            price_raw = await safe_text(card, [
                "span[data-test='div-preco'] > span",
                "[data-test='div-preco']",
                "[class*='price']",
            ])
            if not price_raw:
                return None

            price_raw = price_raw.replace("R$", "").replace(".", "").replace(",", ".").strip()
            try:
                price = float(price_raw)
            except ValueError:
                return None

            listing_preview = {"title": title, "price": price}
            floor = get_price_floor(listing_preview)
            if price < floor:
                return None

            url = await safe_attr(card, [
                "a[href*='/p/']",
                "a[href]",
            ], "href")
            if url and not url.startswith("http"):
                url = f"https://www.enjoei.com.br{url}"

            img = await safe_attr(card, [
                "img[data-test='image-prod']",
                "img[class*='product']",
                "img",
            ], "src") or await safe_attr(card, [
                "img[data-test='image-prod']",
                "img",
            ], "data-src") or ""

            item_id = url.split("/")[-1].split("?")[0] if url else str(abs(hash(title)))

            return self._normalize({
                "id": item_id,
                "title": title,
                "description": "",
                "price": price,
                "url": url or "",
                "images": [img] if img else [],
                "seller_ratings": 0,
                "seller_positive_pct": 100,
            })
        except Exception:
            return None
