import logging

from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode

from analysis.score_engine import Recommendation, ScoreReport
from config.settings import settings
from .formatter import format_daily_report, format_telegram

logger = logging.getLogger(__name__)
bot = Bot(token=settings.telegram_bot_token)


async def send_opportunity(report: ScoreReport, listing_url: str, images: list = None):
    if report.recommendation == Recommendation.REFUSE:
        return

    message = format_telegram(report)
    buttons = [[InlineKeyboardButton("Ver anúncio 🔗", url=listing_url)]]

    if report.recommendation == Recommendation.NEGOTIATE and report.suggested_offer:
        buttons[0].append(
            InlineKeyboardButton(
                f"Oferecer R${report.suggested_offer:.0f}",
                callback_data=f"offer_{report.listing_id}",
            )
        )

    if report.recommendation == Recommendation.FLAG_AUTHENTICATOR:
        buttons.append(
            [InlineKeyboardButton("Marcar autenticador 📋",
                                  callback_data=f"auth_{report.listing_id}")]
        )

    markup = InlineKeyboardMarkup(buttons)

    try:
        # Tenta enviar com foto inline se disponível
        if images and images[0] and images[0].startswith("http"):
            try:
                await bot.send_photo(
                    chat_id=settings.telegram_chat_id,
                    photo=images[0],
                    caption=message[:1024],
                    parse_mode=ParseMode.HTML,
                    reply_markup=markup,
                )
                logger.info(f"[Telegram] Foto enviada: {report.recommendation.value} score={report.total_score}")
                return
            except Exception as photo_err:
                logger.warning(f"[Telegram] Foto falhou, usando texto: {photo_err}")

        await bot.send_message(
            chat_id=settings.telegram_chat_id,
            text=message,
            parse_mode=ParseMode.HTML,
            reply_markup=markup,
        )
        logger.info(f"[Telegram] Mensagem enviada: {report.recommendation.value} score={report.total_score}")
    except Exception as e:
        logger.error(f"[Telegram] ERRO ao enviar — token válido? chat_id correto? Erro: {e}")


async def send_price_drop_alert(drop: dict):
    """Notifica quando item NEGOCIAR cai de preço abaixo da oferta sugerida."""
    pct = drop.get("drop_pct", 0)
    text = (
        f"<b>📉 QUEDA DE PREÇO DETECTADA</b>\n\n"
        f"📦 {drop.get('title', '')}\n\n"
        f"💰 Era: R$ {drop.get('original_price', 0):.0f}\n"
        f"✅ Agora: R$ {drop.get('current_price', 0):.0f} "
        f"({pct:.1%} de queda)\n"
        f"🎯 Sua oferta era: R$ {drop.get('suggested_offer', 0):.0f}\n\n"
        f"<b>Preço atingiu o alvo — hora de comprar!</b>"
    )
    buttons = [[InlineKeyboardButton("Ver anúncio 🔗", url=drop.get("url", ""))]]
    try:
        await bot.send_message(
            chat_id=settings.telegram_chat_id,
            text=text,
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(buttons),
        )
    except Exception as e:
        logger.error(f"Telegram price_drop_alert: {e}")


async def send_daily_report(stats: dict):
    try:
        await bot.send_message(
            chat_id=settings.telegram_chat_id,
            text=format_daily_report(stats),
            parse_mode=ParseMode.HTML,
        )
    except Exception as e:
        logger.error(f"Telegram daily report: {e}")


async def send_health_alert(message: str):
    try:
        await bot.send_message(
            chat_id=settings.telegram_chat_id,
            text=f"<b>⚠️ Health Alert</b>\n{message}",
            parse_mode=ParseMode.HTML,
        )
    except Exception as e:
        logger.error(f"Telegram health alert: {e}")
