"""
Comparáveis do Hunter Scout — mostra outras camisas parecidas com preço e
link real, pra calibrar a avaliação e dar contexto de mercado ao usuário.

Duas fontes combinadas, nenhuma depende de web search de IA (que está gated
atrás de tier pago no Gemini e não temos como validar/depender agora):

1. Banco próprio (Listing) — tudo que o radar de scraping já viu passar,
   sem custo nenhum, sempre disponível.
2. Busca ao vivo no Vinted — API pública, sem auth, testada e funcionando;
   dá link real de oferta disponível agora, não só histórico.

find_comparables recebe uma lista de termos livre (não só jogador+clube) —
isso importa pra itens sem jogador único identificado (ex: "elenco todo
autografado", "centenário 1995"), onde o que diferencia o preço é o
contexto histórico/coletivo, não um nome de jogador.
"""
import logging

import httpx
from sqlalchemy import desc, or_, select

from database.db import AsyncSessionLocal
from database.models import Listing
from scout.schemas import Comparable

logger = logging.getLogger(__name__)

_DB_LIMIT = 4
_VINTED_LIMIT = 4
_VINTED_CURRENCY_TO_BRL = 5.50  # EUR


def _clean_terms(terms: list[str]) -> list[str]:
    return [t.strip() for t in terms if t and t.strip()]


async def _find_db_comparables(terms: list[str]) -> list[Comparable]:
    if not terms:
        return []

    async with AsyncSessionLocal() as session:
        q = (
            select(Listing)
            .where(or_(*[Listing.title.ilike(f"%{t}%") for t in terms]))
            .where(Listing.recommendation != "RECUSAR")
            .order_by(desc(Listing.created_at))
            .limit(_DB_LIMIT)
        )
        rows = (await session.execute(q)).scalars().all()

    return [
        Comparable(
            title=r.title or "",
            price=r.price or 0,
            url=r.url or "",
            platform=r.platform or "",
            source="radar",
        )
        for r in rows
    ]


async def _find_vinted_comparables(terms: list[str]) -> list[Comparable]:
    query = " ".join(terms).strip()
    if not query:
        return []

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            await client.get("https://www.vinted.fr")
            resp = await client.get(
                "https://www.vinted.fr/api/v2/catalog/items",
                params={"search_text": query, "per_page": _VINTED_LIMIT, "order": "relevance"},
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
                    ),
                    "Accept": "application/json",
                },
            )
            if resp.status_code != 200:
                return []
            items = resp.json().get("items", [])
    except Exception as e:
        logger.warning(f"[Scout Comparables] Vinted falhou: {e}")
        return []

    comps = []
    for item in items[:_VINTED_LIMIT]:
        title = item.get("title", "")
        raw_price = item.get("price", 0)
        if isinstance(raw_price, dict):
            raw_price = raw_price.get("amount", 0)
        try:
            price_brl = float(str(raw_price).replace(",", ".")) * _VINTED_CURRENCY_TO_BRL
        except (ValueError, TypeError):
            price_brl = 0
        url = item.get("url", "")
        if url and not url.startswith("http"):
            url = "https://www.vinted.fr" + url
        if title and url:
            comps.append(Comparable(title=title, price=price_brl, url=url, platform="vinted", source="vinted_live"))

    return comps


async def find_comparables(*term_groups: str) -> list[Comparable]:
    """
    Aceita qualquer quantidade de termos de busca livre (jogador, clube,
    ano/era, "elenco", palavras da pergunta do usuário, etc.) — nunca lança,
    combina banco próprio + Vinted ao vivo, tolerando falha de qualquer uma.
    """
    terms = _clean_terms(list(term_groups))
    if not terms:
        return []

    db_comps: list[Comparable] = []
    vinted_comps: list[Comparable] = []

    try:
        db_comps = await _find_db_comparables(terms)
    except Exception as e:
        logger.warning(f"[Scout Comparables] Busca no banco falhou: {e}")

    try:
        vinted_terms = terms + (["signed jersey"] if "signed" not in " ".join(terms).lower() else [])
        vinted_comps = await _find_vinted_comparables(vinted_terms)
    except Exception as e:
        logger.warning(f"[Scout Comparables] Busca Vinted falhou: {e}")

    return db_comps + vinted_comps
