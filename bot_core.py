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
from database.models import Listing, RunLog
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
    OLXScraper(),
    ShopeeScraper(),
    # EnjoeiScraper(),  # pausado — retorna catálogo inteiro sem filtro temporal
    # VintedScraper(),  # pausado — 3 países × 14 termos × 96 itens = muito volume
    # EbayScraper(),
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

    # Dedup ANTES de qualquer chamada de AI — itens já vistos são descartados sem custo
    external_id = listing.get("external_id", "")
    if external_id:
        async with AsyncSessionLocal() as session:
            from sqlalchemy import select as sa_select
            existing = (await session.execute(
                sa_select(Listing.id).where(Listing.external_id == external_id).limit(1)
            )).first()
            if existing:
                return

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

    async with AsyncSessionLocal() as session:

        filters_json = json.dumps([
            {"name": f.name, "score": f.score, "max_score": f.max_score,
             "status": f.status, "detail": f.detail}
            for f in report.filters
        ])
        red_flags_json = json.dumps([
            {"code": f.code, "description": f.description}
            for f in report.red_flags
        ])

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
            filters_json=filters_json,
            red_flags=red_flags_json,
            reasoning=report.reasoning,
            suggested_offer=report.suggested_offer,
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


_COLLECTOR_SIGNALS = [
    # Autógrafo
    "autografad", "autógrafo", "autografo", "autograf", "assinad", "firmad",
    "signed", "autographed", "signe",
    # Match worn
    "match worn", "usada em jogo", "usada no jogo", "player worn", "game worn",
    "match issue", "player issue",
    # Certificação
    "coa", "psa", "beckett", "jsa", "certificad", "hologram", "holograma",
    # Era/vintage
    "retrô", "retro", "vintage", "anos 80", "anos 90", "anos 70",
    "1970", "1971", "1972", "1973", "1974", "1975", "1976", "1977", "1978", "1979",
    "1980", "1981", "1982", "1983", "1984", "1985", "1986", "1987", "1988", "1989",
    "1990", "1991", "1992", "1993", "1994", "1995", "1996", "1997", "1998", "1999",
    "2000", "2001", "2002", "2003", "2004", "2005", "2006",
    # Competições históricas
    "copa do mundo", "world cup", "copa america", "copa america",
    "champions league", "eurocopa", "libertadores",
    # Jogadores icônicos
    "pelé", "pele", "maradona", "zico", "sócrates", "socrates",
    "romário", "romario", "ronaldo fenômeno", "ronaldinho", "cafu",
    "roberto carlos", "garrincha", "rivaldo", "bebeto",
    "messi", "neymar", "cristiano", "cr7", "ronaldo r9",
    "michael jordan", "kobe", "lebron", "magic johnson", "larry bird",
    "scottie pippen", "shaquille", "shaq",
    # Termos colecionador
    "edição limitada", "limited edition", "rara", "raro", "colecionável",
    "original", "autentic", "authentic", "elenco", "squad signed",
]


def _has_collector_signal(listing: dict) -> bool:
    """Pré-filtro barato (CPU-only). False = não vale chamar a AI."""
    title = (listing.get("title") or "").lower()
    price = listing.get("price", 0) or 0
    if price < 80:
        return False
    return any(s in title for s in _COLLECTOR_SIGNALS)


async def run_hunter_cycle():
    logger.info("=== Hunter cycle iniciado ===")
    cycle_new = 0
    cycle_opps_start = stats.get("opportunities", 0)

    # Registra início no RunLog
    run_log_id = None
    try:
        async with AsyncSessionLocal() as session:
            run_log = RunLog(started_at=datetime.utcnow(), status="running", listings_scraped=0)
            session.add(run_log)
            await session.commit()
            await session.refresh(run_log)
            run_log_id = run_log.id
    except Exception as e:
        logger.warning(f"[RunLog] Erro ao criar: {e}")

    for scraper in scrapers:
        listings = await scraper.run()
        cycle_new += len(listings)
        stats["new"] += len(listings)

        for listing in listings:
            try:
                if not _has_collector_signal(listing):
                    logger.debug(f"[Skip] Sem sinal colecionador: {listing.get('title', '')[:50]}")
                    continue
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

    cycle_opps = stats.get("opportunities", 0) - cycle_opps_start

    # Atualiza RunLog com resultado
    if run_log_id:
        try:
            async with AsyncSessionLocal() as session:
                from sqlalchemy import select as sa_select
                run = (await session.execute(
                    sa_select(RunLog).where(RunLog.id == run_log_id)
                )).scalar_one_or_none()
                if run:
                    run.finished_at = datetime.utcnow()
                    run.listings_scraped = cycle_new
                    run.opportunities_found = cycle_opps
                    run.status = "ok"
                    await session.commit()
        except Exception as e:
            logger.warning(f"[RunLog] Erro ao atualizar: {e}")

    logger.info(
        f"=== Cycle concluído: {cycle_new} brutos | "
        f"{cycle_opps} oportunidades | "
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
