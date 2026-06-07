import logging

import httpx

from analysis.score_engine import Recommendation, ScoreReport
from config.settings import settings

logger = logging.getLogger(__name__)

ICONS = {
    Recommendation.BUY_NOW: "🟢",
    Recommendation.NEGOTIATE: "🟡",
    Recommendation.FLAG_AUTHENTICATOR: "🔵",
    Recommendation.REFUSE: "🔴",
}


def _format_message(report: ScoreReport, listing_url: str) -> str:
    icon = ICONS.get(report.recommendation, "⚪")
    lines = [
        f"{icon} *HUNTER MASTER — {report.recommendation.value}*",
        f"Score: {report.total_score}/100",
        "",
        f"📦 {report.title}",
        "",
        f"💰 Compra: R$ {report.buy_price:.0f}",
        f"📈 Venda est.: R$ {report.sell_price_estimate:.0f}",
        f"📊 Margem: {report.gross_margin:.1%}",
    ]

    if report.suggested_offer:
        lines.append(f"🤝 Oferecer: R$ {report.suggested_offer:.0f}")

    lines += ["", f"_{report.reasoning}_", "", f"🔗 {listing_url}"]
    return "\n".join(lines)


async def send_whatsapp(report: ScoreReport, listing_url: str):
    if not settings.evolution_api_url or not settings.evolution_instance:
        return

    message = _format_message(report, listing_url)
    url = (
        f"{settings.evolution_api_url.rstrip('/')}"
        f"/message/sendText/{settings.evolution_instance}"
    )

    payload = {
        "number": settings.whatsapp_number,
        "text": message,
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                url,
                json=payload,
                headers={"apikey": settings.evolution_api_key},
            )
            resp.raise_for_status()
            logger.info(f"WhatsApp enviado para {settings.whatsapp_number}")
    except Exception as e:
        logger.error(f"WhatsApp send falhou: {e}")


async def send_whatsapp_daily_report(stats: dict):
    if not settings.evolution_api_url or not settings.evolution_instance:
        return

    lines = [
        "📊 *RELATÓRIO DIÁRIO — Hunter Master*",
        "",
        f"🔍 Varridos: {stats.get('scraped', 0)}",
        f"🆕 Novos: {stats.get('new', 0)}",
        f"✨ Oportunidades: {stats.get('opportunities', 0)}",
        "",
        f"🟢 COMPRAR: {stats.get('buy', 0)}",
        f"🟡 NEGOCIAR: {stats.get('negotiate', 0)}",
        f"🔵 AUTENTICADOR: {stats.get('flag', 0)}",
        f"🔴 RECUSAR: {stats.get('refuse', 0)}",
    ]

    if stats.get("errors"):
        lines += ["", f"⚠️ Erros: {', '.join(stats['errors'])}"]

    url = (
        f"{settings.evolution_api_url.rstrip('/')}"
        f"/message/sendText/{settings.evolution_instance}"
    )

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                url,
                json={"number": settings.whatsapp_number, "text": "\n".join(lines)},
                headers={"apikey": settings.evolution_api_key},
            )
            resp.raise_for_status()
    except Exception as e:
        logger.error(f"WhatsApp daily report falhou: {e}")
