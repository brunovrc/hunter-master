import asyncio
import logging

from playwright.async_api import async_playwright

from .base import BaseScraper, is_recent, _UNKNOWN_TS

logger = logging.getLogger(__name__)

# sf=1 = mais recentes primeiro na OLX
OLX_URLS = [
    "https://www.olx.com.br/esportes-e-lazer?q=camisa+futebol+autografada&sf=1",
    "https://www.olx.com.br/esportes-e-lazer?q=camisa+futebol+assinada+jogador&sf=1",
    "https://www.olx.com.br/esportes-e-lazer?q=camisa+futebol+match+worn&sf=1",
    "https://www.olx.com.br/esportes-e-lazer?q=camisa+futebol+autografada+COA&sf=1",
    "https://www.olx.com.br/esportes-e-lazer?q=camisa+nba+autografada&sf=1",
    "https://www.olx.com.br/esportes-e-lazer?q=camisa+basquete+autografada&sf=1",
]

_MAX_CARDS = 20


class OLXScraper(BaseScraper):
    name = "olx"

    async def scrape(self) -> list:
        listings = []

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                )
            )
            page = await context.new_page()

            for url in OLX_URLS:
                try:
                    await page.goto(url, wait_until="domcontentloaded", timeout=60000)
                    await asyncio.sleep(2)

                    cards = await page.query_selector_all(
                        "[data-ds-component='DS-AdCard'], "
                        "[data-lurker-detail='result_card'], "
                        "li[data-lurker-detail]"
                    )

                    for card in cards[:_MAX_CARDS]:
                        parsed = await self._parse_card(card)
                        if parsed:
                            listings.append(parsed)

                    await asyncio.sleep(3)
                except Exception as e:
                    logger.warning(f"[OLX] {url} falhou: {e}")

            await browser.close()

        return listings

    async def _parse_card(self, card) -> dict | None:
        try:
            title_el = await card.query_selector("h2, [class*='title'], [data-lurker-detail='title']")
            price_el = await card.query_selector("[class*='price'], [data-lurker-detail='price']")
            link_el = await card.query_selector("a")
            img_el = await card.query_selector("img")

            if not title_el or not price_el:
                return None

            title = (await title_el.inner_text()).strip()
            price_raw = (await price_el.inner_text()).strip()
            price_raw = price_raw.replace("R$", "").replace(".", "").replace(",", ".").strip()

            try:
                price = float(price_raw)
            except ValueError:
                return None

            if price < 80:
                return None

            url = await link_el.get_attribute("href") if link_el else ""
            img = await img_el.get_attribute("src") if img_el else ""
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
                "listed_at": _UNKNOWN_TS,
            })
        except Exception:
            return None
