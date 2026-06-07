import logging
import re

import httpx
from bs4 import BeautifulSoup

from database.db import AsyncSessionLocal
from database.models import Tier3Price

logger = logging.getLogger(__name__)

TIER3_SOURCES = [
    {
        "name": "sr_futebol",
        "url": "https://www.srfutebol.com.br/camisas-autografadas",
        "title_selector": "h2, .product-title, [class*='title']",
        "price_selector": ".price, .valor, [class*='price']",
    },
    {
        "name": "brecho_futebol",
        "url": "https://www.brechodofutebol.com.br",
        "title_selector": "h2, .product-name",
        "price_selector": ".price",
    },
]

PLAYER_MAP = {
    "zico": "Zico",
    "ronaldo": "Ronaldo Fenômeno",
    "romário": "Romário",
    "pelé": "Pelé",
    "sócrates": "Sócrates",
    "neymar": "Neymar",
    "senna": "Senna",
    "schumacher": "Schumacher",
}

CLUB_MAP = {
    "flamengo": "Flamengo",
    "santos": "Santos",
    "corinthians": "Corinthians",
    "ferrari": "Ferrari",
    "mclaren": "McLaren",
}


async def scrape_tier3_prices():
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
    }
    async with httpx.AsyncClient(headers=headers, timeout=30, follow_redirects=True) as client:
        for source in TIER3_SOURCES:
            try:
                resp = await client.get(source["url"])
                if resp.status_code != 200:
                    continue

                soup = BeautifulSoup(resp.text, "lxml")
                titles = soup.select(source["title_selector"])
                prices_els = soup.select(source["price_selector"])
                items = []

                for title_el, price_el in zip(titles, prices_els):
                    title = title_el.get_text(strip=True)
                    price_raw = price_el.get_text(strip=True)
                    price_match = re.search(r"[\d]+[,.]?[\d]*", price_raw.replace(".", "").replace(",", "."))
                    if not price_match:
                        continue
                    try:
                        price = float(price_match.group().replace(",", "."))
                        if price < 50:
                            continue
                        items.append(
                            Tier3Price(
                                player_name=_extract_player(title),
                                club=_extract_club(title),
                                item_type=_extract_type(title),
                                price=price,
                                source=source["name"],
                                url=source["url"],
                            )
                        )
                    except ValueError:
                        continue

                async with AsyncSessionLocal() as session:
                    session.add_all(items)
                    await session.commit()

                logger.info(f"[Tier3] {source['name']}: {len(items)} preços coletados")
            except Exception as e:
                logger.warning(f"[Tier3] {source['name']} falhou: {e}")


def _extract_player(title: str) -> str:
    t = title.lower()
    for key, name in PLAYER_MAP.items():
        if key in t:
            return name
    return ""


def _extract_club(title: str) -> str:
    t = title.lower()
    for key, name in CLUB_MAP.items():
        if key in t:
            return name
    return ""


def _extract_type(title: str) -> str:
    t = title.lower()
    if "autograf" in t:
        return "autografada"
    if "match worn" in t or "jogo" in t:
        return "match_worn"
    return "retro"
