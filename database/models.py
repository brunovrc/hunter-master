from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Listing(Base):
    __tablename__ = "listings"

    id = Column(Integer, primary_key=True)
    external_id = Column(String, unique=True, index=True)
    platform = Column(String, index=True)
    url = Column(String)
    title = Column(String, index=True)
    description = Column(Text)
    price = Column(Float)
    seller_id = Column(String)
    seller_name = Column(String)
    seller_ratings = Column(Integer, default=0)
    seller_positive_pct = Column(Float, default=100)
    images = Column(Text)  # JSON

    score = Column(Integer, default=0)
    recommendation = Column(String, index=True)
    gross_margin = Column(Float)
    sell_price_estimate = Column(Float)

    player_name = Column(String, index=True)
    club = Column(String)
    year_era = Column(String)
    is_autographed = Column(Boolean, default=False)
    is_match_worn = Column(Boolean, default=False)
    has_coa = Column(Boolean, default=False)

    red_flags = Column(Text)  # JSON
    notified = Column(Boolean, default=False)

    # Dedup cross-platform: hash do título normalizado
    title_hash = Column(String, index=True)

    # Dashboard actions
    purchased = Column(Boolean, default=False)
    purchased_at = Column(DateTime, nullable=True)
    purchase_notes = Column(Text, nullable=True)
    discarded = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Tier3Price(Base):
    __tablename__ = "tier3_prices"

    id = Column(Integer, primary_key=True)
    player_name = Column(String, index=True)
    club = Column(String)
    item_type = Column(String)  # autografada, retro, match_worn
    price = Column(Float)
    source = Column(String)
    url = Column(String)
    scraped_at = Column(DateTime, default=datetime.utcnow)


class RunLog(Base):
    __tablename__ = "run_logs"

    id = Column(Integer, primary_key=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime)
    listings_scraped = Column(Integer, default=0)
    listings_analyzed = Column(Integer, default=0)
    opportunities_found = Column(Integer, default=0)
    errors = Column(Text)  # JSON
    status = Column(String, default="running")


class LiquidityScore(Base):
    """
    Score de liquidez por atleta: estimativa de velocidade de venda.
    Calculado a partir do histórico de aparições + preços no Tier3.
    """
    __tablename__ = "liquidity_scores"

    id = Column(Integer, primary_key=True)
    player_slug = Column(String, unique=True, index=True)
    player_name = Column(String)
    avg_days_to_sell = Column(Float)         # média estimada de dias para vender
    total_listings_seen = Column(Integer, default=0)
    avg_sell_price = Column(Float)
    last_calculated = Column(DateTime, default=datetime.utcnow)


class PriceWatch(Base):
    """
    Monitoramento de queda de preço em itens recomendados NEGOCIAR.
    Re-checados a cada ciclo para detectar quando o preço cai abaixo da oferta sugerida.
    """
    __tablename__ = "price_watches"

    id = Column(Integer, primary_key=True)
    external_id = Column(String, index=True)
    platform = Column(String)
    url = Column(String)
    title = Column(String)
    original_price = Column(Float)
    suggested_offer = Column(Float)
    current_price = Column(Float)
    last_checked = Column(DateTime, default=datetime.utcnow)
    notified_drop = Column(Boolean, default=False)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class RarityIndex(Base):
    """
    Índice de raridade baseado no histórico do próprio banco.
    Quanto mais vezes um item similar aparece → menos raro → menor score.
    """
    __tablename__ = "rarity_index"

    id = Column(Integer, primary_key=True)
    item_signature = Column(String, unique=True, index=True)  # slug: player+type+era
    appearances_30d = Column(Integer, default=0)   # aparições nos últimos 30 dias
    appearances_90d = Column(Integer, default=0)
    last_seen = Column(DateTime)
    rarity_score = Column(Float, default=50.0)     # 0=commodity, 100=único
    last_updated = Column(DateTime, default=datetime.utcnow)
