"""
Monitor de queda de preço para itens na fila NEGOCIAR.
Re-checa o preço via Playwright a cada ciclo.
Se o preço cair abaixo da oferta sugerida → notifica como COMPRAR AGORA.
"""

import logging
from datetime import datetime

import httpx
from sqlalchemy import select

from .db import AsyncSessionLocal
from .models import PriceWatch

logger = logging.getLogger(__name__)


async def add_to_watch(
    external_id: str,
    platform: str,
    url: str,
    title: str,
    original_price: float,
    suggested_offer: float,
):
    """Adiciona item NEGOCIAR à lista de monitoramento."""
    async with AsyncSessionLocal() as session:
        existing = (await session.execute(
            select(PriceWatch).where(PriceWatch.external_id == external_id)
        )).scalar_one_or_none()

        if existing:
            existing.original_price = original_price
            existing.suggested_offer = suggested_offer
            existing.active = True
        else:
            session.add(PriceWatch(
                external_id=external_id,
                platform=platform,
                url=url,
                title=title,
                original_price=original_price,
                suggested_offer=suggested_offer,
                current_price=original_price,
            ))
        await session.commit()
        logger.info(f"[PriceWatch] Monitorando: {title[:50]} | Oferta: R${suggested_offer:.0f}")


async def check_price_drops() -> list[dict]:
    """
    Verifica queda de preço em todos os itens ativos no PriceWatch.
    Retorna lista de itens com queda significativa (≥10%) para notificar.
    """
    drops = []
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(PriceWatch).where(
                PriceWatch.active == True,
                PriceWatch.notified_drop == False,
            )
        )
        watches = result.scalars().all()

    for watch in watches:
        try:
            new_price = await _fetch_current_price(watch.url, watch.platform)
            if new_price is None:
                continue

            async with AsyncSessionLocal() as session:
                obj = (await session.execute(
                    select(PriceWatch).where(PriceWatch.id == watch.id)
                )).scalar_one()
                obj.current_price = new_price
                obj.last_checked = datetime.utcnow()

                # Queda abaixo ou igual à oferta sugerida → oportunidade
                if new_price <= watch.suggested_offer:
                    obj.notified_drop = True
                    obj.active = False
                    drops.append({
                        "title": watch.title,
                        "url": watch.url,
                        "original_price": watch.original_price,
                        "current_price": new_price,
                        "suggested_offer": watch.suggested_offer,
                        "drop_pct": (watch.original_price - new_price) / watch.original_price,
                    })
                    logger.info(
                        f"[PriceWatch] QUEDA DETECTADA: {watch.title[:40]} "
                        f"R${watch.original_price:.0f} → R${new_price:.0f}"
                    )
                elif new_price < watch.original_price * 0.90:
                    # Queda >10% mas ainda acima da oferta — atualiza e mantém monitoramento
                    logger.info(
                        f"[PriceWatch] Queda parcial: {watch.title[:40]} "
                        f"R${watch.original_price:.0f} → R${new_price:.0f} (ainda acima da oferta)"
                    )

                await session.commit()

        except Exception as e:
            logger.warning(f"[PriceWatch] Erro ao checar {watch.url[:60]}: {e}")

    return drops


async def _fetch_current_price(url: str, platform: str) -> float | None:
    """
    Busca o preço atual da URL via httpx (leve, sem Playwright).
    Para ML e Enjoei, o preço aparece no HTML mesmo sem JS em alguns casos.
    Fallback: retorna None se não conseguir.
    """
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "pt-BR,pt;q=0.9",
        }
        async with httpx.AsyncClient(headers=headers, timeout=15, follow_redirects=True) as client:
            resp = await client.get(url)
            if resp.status_code != 200:
                return None

            text = resp.text

            # Heurística: busca padrão de preço no HTML
            import re
            # ML pattern: "price":1234.56 ou similar
            patterns = [
                r'"price":\s*([\d]+(?:\.\d+)?)',
                r'"selling_price":\s*([\d]+(?:\.\d+)?)',
                r'data-price="([\d]+(?:[.,]\d+)?)"',
                r'class="[^"]*price[^"]*"[^>]*>([\d.,]+)',
            ]
            for pat in patterns:
                match = re.search(pat, text)
                if match:
                    raw = match.group(1).replace(".", "").replace(",", ".")
                    try:
                        price = float(raw)
                        if 50 < price < 1_000_000:
                            return price
                    except ValueError:
                        continue

    except Exception:
        pass
    return None


async def deactivate_watch(external_id: str):
    """Desativa monitoramento quando item é comprado ou removido."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(PriceWatch).where(PriceWatch.external_id == external_id)
        )
        obj = result.scalar_one_or_none()
        if obj:
            obj.active = False
            await session.commit()
