"""
Índice de raridade baseado no histórico do próprio banco.
Quanto menos vezes um item similar apareceu nos últimos 90 dias → mais raro.
"""

import hashlib
import logging
from datetime import datetime, timedelta

from sqlalchemy import func, select

from .db import AsyncSessionLocal
from .models import Listing, RarityIndex

logger = logging.getLogger(__name__)


def make_item_signature(player_name: str, item_type: str, era: str = "") -> str:
    """Cria um slug único para o item: player + type + era."""
    parts = [
        player_name.lower().strip(),
        item_type.lower().strip(),
        era.lower().strip() if era else "",
    ]
    raw = "_".join(p for p in parts if p)
    return hashlib.md5(raw.encode()).hexdigest()[:12]


async def get_rarity_score(player_name: str, item_type: str, era: str = "") -> float:
    """
    Retorna score de raridade (0–100).
    100 = nunca visto antes (raríssimo)
    50  = aparece esporadicamente
    0   = commodity (aparece toda semana)
    """
    sig = make_item_signature(player_name, item_type, era)

    async with AsyncSessionLocal() as session:
        # Busca no índice de raridade
        result = await session.execute(
            select(RarityIndex).where(RarityIndex.item_signature == sig)
        )
        rarity = result.scalar_one_or_none()

        if rarity:
            return rarity.rarity_score

        # Sem histórico → item nunca visto → raridade alta
        return 85.0


async def update_rarity_index(player_name: str, item_type: str, era: str = ""):
    """
    Registra aparição do item e recalcula o score de raridade.
    Chamado sempre que um item passa pelo pipeline de análise.
    """
    sig = make_item_signature(player_name, item_type, era)
    now = datetime.utcnow()
    cutoff_30d = now - timedelta(days=30)
    cutoff_90d = now - timedelta(days=90)

    async with AsyncSessionLocal() as session:
        # Conta aparições no banco principal
        count_30d = (await session.execute(
            select(func.count(Listing.id)).where(
                Listing.player_name.ilike(f"%{player_name}%") if player_name else Listing.id == -1,
                Listing.created_at >= cutoff_30d,
            )
        )).scalar() or 0

        count_90d = (await session.execute(
            select(func.count(Listing.id)).where(
                Listing.player_name.ilike(f"%{player_name}%") if player_name else Listing.id == -1,
                Listing.created_at >= cutoff_90d,
            )
        )).scalar() or 0

        # Score: inversamente proporcional às aparições
        # 0 em 90d → 85 pts | 1–3 → 70 | 4–10 → 50 | 11–30 → 25 | >30 → 5
        if count_90d == 0:
            score = 85.0
        elif count_90d <= 3:
            score = 70.0
        elif count_90d <= 10:
            score = 50.0
        elif count_90d <= 30:
            score = 25.0
        else:
            score = 5.0

        # Upsert no índice
        existing = (await session.execute(
            select(RarityIndex).where(RarityIndex.item_signature == sig)
        )).scalar_one_or_none()

        if existing:
            existing.appearances_30d = count_30d
            existing.appearances_90d = count_90d
            existing.rarity_score = score
            existing.last_seen = now
            existing.last_updated = now
        else:
            session.add(RarityIndex(
                item_signature=sig,
                appearances_30d=count_30d,
                appearances_90d=count_90d,
                rarity_score=score,
                last_seen=now,
                last_updated=now,
            ))

        await session.commit()
        return score
