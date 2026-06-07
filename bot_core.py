"""
Núcleo do bot Hunter Master.
Separado de main.py para permitir import pelo dashboard sem circular dependency.
"""
import asyncio
import json
import logging
from datetime import datetime

from analysis.claude_analyzer import analyze_images, extract_listing_data
from analysis.red_flags import check_red_flags, has_critical_flag
from analysis.score_engine import Recommendation, run_score_engine
from config.nba import find_nba_player
from config.players import get_player_or_default
from config.settings import settings
from database.db import AsyncSessionLocal
from database.models import Listing
from database.price_monitor import add_to_watch, check_price_drops
from database.price_tracker import get_sell_price_estimate
from database.rarity_index import get_rarity_score, update_rarity_index
from notifications.email_sender import send_opportunity_email
from notifications.telegram_bot import send_daily_report, send_health_alert, send_opportunity, send_price_drop_alert
from notifications.whatsapp import send_whatsapp, send_whatsapp_daily_report
from scrapers.ebay import EbayScraper
from scrapers.enjoei import EnjoeiScraper
from scrapers.vinted import VintedScraper
from scrapers.mercadolivre import MercadoLivreScraper
from scrapers.mercadolivre_argentina import MercadoLivreArgentinaScraper
from scrapers.olx import OLXScraper
from scrapers.shopee import ShopeeScraper
from scrapers.tier3_pricer import scrape_tier3_prices  # noqa: F401 — usado pelo scheduler

logger = logging.getLogger("hunter_master")

scrapers = [
    MercadoLivreScraper(),
    MercadoLivreArgentinaScraper(),
    EnjoeiScraper(),
    OLXScraper(),
    ShopeeScraper(),
    EbayScraper(),
    VintedScraper(),
]

stats = {
    "scraped": 0,
    "new": 0,
    "opportunities": 0,
    "buy": 0,
    "negotiate": 0,
    "flag": 0,
    "refuse": 0,
    "price_drops": 0,
    "errors": [],
}


def _find_player_data(title: str, extracted: dict) -> dict:
    player_name = (extracted.get("player_name") or "").lower()
    title_lower = title.lower()
    if any(k in title_lower for k in ["nba", "basquete", "basketball", "basquet"]):
        nba = find_nba_player(title, player_name)
        if nba:
            return nba
    return get_player_or_default(title, player_name)


async def _process_listing(listing: dict):
    global stats
    stats["scraped"] += 1

    flags = check_red_flags(listing)
    if has_critical_flag(flags):
        return

    extracted = await extract_listing_data(listing)

    if extracted.get("is_personalized_jersey"):
        logger.debug(f"[Pipeline] Personalizada descartada: {listing.get('title', '')[:50]}")
        return

    vision = await analyze_images(listing.get("images", []), listing)
    claude_analysis = {**extracted, **vision}

    if claude_analysis.get("likely_fake") or claude_analysis.get("autopen_suspected"):
        return

    player_name = extracted.get("player_name", "")
    is_autographed = extracted.get("is_autographed", False)
    is_match_worn = extracted.get("is_match_worn", False)

    # Se o título declara autógrafo/match worn, confia para fins de precificação.
    # A IA rejeita fakes antes disso — aqui só queremos o preço correto.
    title_lower = (listing.get("title") or "").lower()
    _AUTO_SIGNALS = ["autografad", "autógrafo", "autografo", "autograf",
                     "assinad", " signed ", "autographed", "signe"]
    _MW_SIGNALS   = ["match worn", "usada em jogo", "usada no jogo",
                     "player worn", "game worn", "match issue"]
    if not is_autographed and any(s in title_lower for s in _AUTO_SIGNALS):
        is_autographed = True
    if not is_match_worn and any(s in title_lower for s in _MW_SIGNALS):
        is_match_worn = True

    item_type = (
        "match_worn" if is_match_worn
        else "autografada" if is_autographed
        else "retro"
    )

    sell_price = await get_sell_price_estimate(player_name, item_type, title=listing.get("title", ""))
    player_data = _find_player_data(listing["title"], extracted)

    era = extracted.get("year_era", "")
    rarity_score = await get_rarity_score(player_name, item_type, era)
    await update_rarity_index(player_name, item_type, era)

    report = run_score_engine(listing, sell_price, player_data, claude_analysis, rarity_score)

    raw_images = listing.get("images", [])
    images_json = json.dumps(raw_images) if isinstance(raw_images, list) else "[]"

    external_id = listing.get("external_id", "")
    async with AsyncSessionLocal() as session:
        from sqlalchemy import select as sa_select
        existing = (await session.execute(
            sa_select(Listing.id).where(Listing.external_id == external_id).limit(1)
        )).first()
        if existing:
            return

        db_listing = Listing(
            external_id=external_id,
            platform=listing.get("platform", ""),
            url=listing.get("url", ""),
            title=listing.get("title", ""),
            price=listing.get("price", 0),
            images=images_json,
            score=report.total_score,
            recommendation=report.recommendation.value,
            gross_margin=report.gross_margin,
            sell_price_estimate=sell_price,
            player_name=player_name,
            is_autographed=is_autographed,
            is_match_worn=is_match_worn,
            has_coa=extracted.get("has_coa", False),
            title_hash=listing.get("title_hash", ""),
        )
        session.add(db_listing)
        await session.commit()

    if report.recommendation == Recommendation.BUY_NOW:
        stats["buy"] += 1
        stats["opportunities"] += 1
    elif report.recommendation == Recommendation.NEGOTIATE:
        stats["negotiate"] += 1
        stats["opportunities"] += 1
        if report.suggested_offer:
            await add_to_watch(
                external_id=listing.get("external_id", ""),
                platform=listing.get("platform", ""),
                url=listing.get("url", ""),
                title=listing.get("title", ""),
                original_price=listing.get("price", 0),
                suggested_offer=report.suggested_offer,
            )
    elif report.recommendation == Recommendation.FLAG_AUTHENTICATOR:
        stats["flag"] += 1
        stats["opportunities"] += 1
    else:
        stats["refuse"] += 1

    if report.recommendation != Recommendation.REFUSE:
        title_hash = listing.get("title_hash", "")
        if title_hash:
            async with AsyncSessionLocal() as session:
                from sqlalchemy import select as sa_select
                already = (await session.execute(
                    sa_select(Listing.notified).where(
                        Listing.title_hash == title_hash,
                        Listing.notified == True,
                    ).limit(1)
                )).first()
                if already:
                    return

        url = listing.get("url", "")
        images = listing.get("images", [])
        await send_opportunity(report, url, images)
        await send_whatsapp(report, url)
        send_opportunity_email(report, url)

        async with AsyncSessionLocal() as session:
            from sqlalchemy import update as sa_update
            await session.execute(
                sa_update(Listing)
                .where(Listing.external_id == listing.get("external_id", ""))
                .values(notified=True)
            )
            await session.commit()

        logger.info(
            f"[Notificado] {report.recommendation.value} | "
            f"score={report.total_score} | R${listing.get('price', 0):.0f} | "
            f"{listing.get('title', '')[:60]}"
        )


async def run_hunter_cycle():
    logger.info("=== Hunter cycle iniciado ===")
    cycle_new = 0

    for scraper in scrapers:
        listings = await scraper.run()
        cycle_new += len(listings)
        stats["new"] += len(listings)

        for listing in listings:
            try:
                await _process_listing(listing)
            except Exception as e:
                logger.error(f"Erro ao processar {listing.get('id')}: {e}")

    try:
        drops = await check_price_drops()
        for drop in drops:
            stats["price_drops"] += 1
            await send_price_drop_alert(drop)
    except Exception as e:
        logger.error(f"Erro no price monitor: {e}")

    logger.info(
        f"=== Cycle concluído: {cycle_new} novos | "
        f"{stats['buy']} COMPRAR | {stats['negotiate']} NEGOCIAR ==="
    )


async def run_daily_report():
    global stats
    await send_daily_report(stats)
    await send_whatsapp_daily_report(stats)
    stats = {k: 0 if isinstance(v, int) else [] for k, v in stats.items()}


async def run_health_check():
    broken = [s.name for s in scrapers if s.circuit_breaker.paused_until]
    if broken:
        await send_health_alert(f"Scrapers com circuit breaker ativo: {', '.join(broken)}")
