import hashlib
import logging
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional

# Anúncios mais velhos que isso são ignorados — radar só quer novidades
_MAX_AGE_MINUTES = 60  # 1h — janela de oportunidade real

_UNKNOWN_TS = object()  # sentinel: scraper não tem timestamp


def is_recent(listed_at) -> bool:
    """True se o anúncio foi criado nos últimos _MAX_AGE_MINUTES minutos.
    Passar is_recent(_UNKNOWN_TS) retorna True (scrapers sem timestamp usam só dedup).
    Passar is_recent(None) retorna False (timestamp esperado mas ausente → rejeita).
    """
    if listed_at is _UNKNOWN_TS:
        return True  # scraper sem timestamp — dedup é o filtro
    if listed_at is None or listed_at == "" or listed_at == 0:
        return False  # timestamp esperado mas ausente/zero → rejeita item antigo
    try:
        if isinstance(listed_at, (int, float)):
            dt = datetime.fromtimestamp(listed_at, tz=timezone.utc)
        elif isinstance(listed_at, str):
            dt = datetime.fromisoformat(listed_at.replace("Z", "+00:00"))
        else:
            dt = listed_at
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - dt).total_seconds() <= _MAX_AGE_MINUTES * 60
    except Exception:
        return False  # parse falhou → rejeita por precaução

from sqlalchemy import select

from database.db import AsyncSessionLocal
from database.models import Listing

logger = logging.getLogger(__name__)


@dataclass
class CircuitBreaker:
    name: str
    max_failures: int = 3
    pause_minutes: int = 60
    failures: int = 0
    paused_until: Optional[datetime] = None

    def is_open(self) -> bool:
        if self.paused_until and datetime.utcnow() < self.paused_until:
            return True
        if self.paused_until and datetime.utcnow() >= self.paused_until:
            self.failures = 0
            self.paused_until = None
        return False

    def record_failure(self):
        self.failures += 1
        if self.failures >= self.max_failures:
            self.paused_until = datetime.utcnow() + timedelta(minutes=self.pause_minutes)
            logger.warning(
                f"[{self.name}] Circuit breaker ativado — pausa de {self.pause_minutes}min"
            )

    def record_success(self):
        self.failures = 0


def _normalize_title(title: str) -> str:
    """
    Normaliza título para deduplicação cross-plataforma.
    Remove palavras de plataforma, tamanhos, pontuação, acentos, caixa.
    """
    t = title.lower()
    # Remove acentos comuns
    for old, new in [("á","a"),("à","a"),("ã","a"),("â","a"),("é","e"),("ê","e"),
                     ("í","i"),("ó","o"),("ô","o"),("õ","o"),("ú","u"),("ü","u"),("ç","c")]:
        t = t.replace(old, new)
    # Remove tamanhos e anos
    t = re.sub(r'\b(p|m|g|gg|xg|xgg|xl|xxl|2xl|3xl|s|l)\b', '', t)
    t = re.sub(r'\b(20\d{2}|19\d{2})\b', '', t)
    # Remove pontuação e espaço extra
    t = re.sub(r'[^\w\s]', ' ', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t


def make_title_hash(title: str) -> str:
    """Hash do título normalizado — igual em plataformas diferentes para o mesmo item."""
    normalized = _normalize_title(title)
    return hashlib.md5(normalized.encode()).hexdigest()[:16]


class BaseScraper:
    name: str = "base"

    def __init__(self):
        self.circuit_breaker = CircuitBreaker(self.name)
        self.seen_ids: set = set()
        self.seen_title_hashes: set = set()  # dedup cross-plataforma em memória

    async def scrape(self) -> list:
        raise NotImplementedError

    async def run(self) -> list:
        if self.circuit_breaker.is_open():
            logger.info(f"[{self.name}] Circuit breaker aberto — pulando")
            return []

        try:
            listings = await self.scrape()
            self.circuit_breaker.record_success()
            new_listings = await self._deduplicate(listings)
            logger.info(
                f"[{self.name}] {len(listings)} coletados, {len(new_listings)} novos"
            )
            return new_listings
        except Exception as e:
            self.circuit_breaker.record_failure()
            logger.error(f"[{self.name}] Erro: {e}")
            return []

    async def _deduplicate(self, listings: list) -> list:
        async with AsyncSessionLocal() as session:
            new_listings = []
            for listing in listings:
                ext_id = f"{self.name}_{listing.get('id')}"

                # 1. Dedup por ID exato (mesma plataforma)
                if ext_id in self.seen_ids:
                    continue

                # 2. Dedup cross-plataforma por hash de título
                title_hash = make_title_hash(listing.get("title", ""))
                if title_hash in self.seen_title_hashes:
                    logger.debug(f"[{self.name}] Duplicata cross-platform detectada: {listing.get('title', '')[:50]}")
                    continue

                # 3. Verifica banco de dados por external_id
                result_id = await session.execute(
                    select(Listing.id).where(Listing.external_id == ext_id).limit(1)
                )
                if result_id.first() is not None:
                    self.seen_ids.add(ext_id)
                    continue

                # 4. Verifica title_hash no banco (cross-platform persistente)
                result_hash = await session.execute(
                    select(Listing.id).where(Listing.title_hash == title_hash).limit(1)
                )
                if result_hash.first() is not None:
                    logger.debug(f"[{self.name}] Duplicata DB cross-platform: {listing.get('title', '')[:50]}")
                    self.seen_title_hashes.add(title_hash)
                    continue

                self.seen_ids.add(ext_id)
                self.seen_title_hashes.add(title_hash)
                listing["external_id"] = ext_id
                listing["platform"] = self.name
                listing["title_hash"] = title_hash
                new_listings.append(listing)

            return new_listings

    @staticmethod
    def _normalize(raw: dict) -> dict:
        return {
            "id": str(raw.get("id", "")),
            "title": raw.get("title", ""),
            "description": raw.get("description", ""),
            "price": float(raw.get("price", 0)),
            "url": raw.get("url", ""),
            "images": raw.get("images", []),
            "seller": {
                "id": str(raw.get("seller_id", "")),
                "name": raw.get("seller_name", ""),
                "total_ratings": int(raw.get("seller_ratings", 0)),
                "positive_pct": float(raw.get("seller_positive_pct", 100)),
            },
        }
