from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from .red_flags import check_red_flags, has_critical_flag, calculate_flag_penalty
from config.jerseys_catalog import find_catalog_match


class Recommendation(Enum):
    BUY_NOW = "COMPRAR AGORA"
    NEGOTIATE = "NEGOCIAR"
    FLAG_AUTHENTICATOR = "FLAG AUTENTICADOR"
    REFUSE = "RECUSAR"


@dataclass
class FilterResult:
    name: str
    score: int
    max_score: int
    status: str  # VERDE, AMARELO, VERMELHO
    detail: str


@dataclass
class ScoreReport:
    listing_id: str
    title: str
    buy_price: float
    sell_price_estimate: float
    gross_margin: float
    absolute_profit: float
    filters: list
    red_flags: list
    total_score: int
    recommendation: Recommendation
    suggested_offer: Optional[float]
    reasoning: str


# ── Lucro absoluto mínimo ─────────────────────────────────────────────────────
MIN_ABSOLUTE_PROFIT = 300   # R$ — abaixo disso não vale o esforço operacional


def calculate_gross_margin(buy_price: float, sell_price: float) -> float:
    if sell_price <= 0:
        return 0.0
    return (sell_price - buy_price) / sell_price


# ── F1: Margem bruta + lucro absoluto ─────────────────────────────────────────

def score_f1_margin(margin: float, buy_price: float, sell_price: float) -> FilterResult:
    profit = sell_price - buy_price

    if profit < MIN_ABSOLUTE_PROFIT:
        return FilterResult(
            "Margem / Lucro", 0, 30, "VERMELHO",
            f"Lucro absoluto R${profit:.0f} abaixo do mínimo (R${MIN_ABSOLUTE_PROFIT})"
        )

    if margin >= 0.40:
        return FilterResult("Margem / Lucro", 30, 30, "VERDE",
                            f"Margem {margin:.1%} | Lucro R${profit:.0f}")
    elif margin >= 0.20:
        return FilterResult("Margem / Lucro", 15, 30, "AMARELO",
                            f"Margem {margin:.1%} | Lucro R${profit:.0f} — negociação recomendada")
    else:
        return FilterResult("Margem / Lucro", 0, 30, "VERMELHO",
                            f"Margem {margin:.1%} insuficiente")


# ── F2: Autenticidade ─────────────────────────────────────────────────────────

def score_f2_authenticity(listing: dict, claude_analysis: dict) -> FilterResult:
    coa_keywords = ["psa", "beckett", "jsa", "sb brasil", "fabricks", "coa", "certificado"]
    text = f"{listing.get('title', '')} {listing.get('description', '')}".lower()

    has_coa = any(k in text for k in coa_keywords)
    has_coa_ai = claude_analysis.get("has_coa", False)
    coa_type = claude_analysis.get("coa_type", "")
    auth_score = claude_analysis.get("authenticity_score", 50)

    if (has_coa or has_coa_ai) and auth_score >= 70:
        detail = f"COA verificado ({coa_type or 'mencionado'}) + análise IA positiva ({auth_score}/100)"
        return FilterResult("Autenticidade", 25, 25, "VERDE", detail)
    elif has_coa or auth_score >= 65:
        return FilterResult("Autenticidade", 15, 25, "AMARELO",
                            f"COA parcial | IA: {auth_score}/100 — autenticador recomendado")
    elif auth_score >= 50:
        return FilterResult("Autenticidade", 8, 25, "AMARELO",
                            f"Sem COA verificável | IA: {auth_score}/100")
    else:
        return FilterResult("Autenticidade", 0, 25, "VERMELHO",
                            f"Sem COA + suspeita de falsidade (IA: {auth_score}/100)")


# ── F3: Turnover / Liquidez ───────────────────────────────────────────────────

def score_f3_turnover(listing: dict, player_data: dict) -> FilterResult:
    from config.nba import get_nba_season_boost
    rarity = player_data.get("raridade", "regional")
    liquidez_dias = player_data.get("liquidez_dias", 180)
    title_lower = listing.get("title", "").lower()
    is_match_worn = any(k in title_lower for k in [
        "match worn", "jogo", "usada em jogo", "usada en partido"
    ])
    is_nba = any(k in title_lower for k in ["nba", "basquete", "basketball", "basquet"])

    # Boost sazonal NBA
    nba_phase, nba_boost = get_nba_season_boost()
    nba_boost_applied = nba_boost // 4 if is_nba else 0  # converte % → pontos

    if rarity == "icon" or liquidez_dias <= 14:
        score = 15
        detail = f"Liquidez alta — giro estimado ≤{liquidez_dias}d (ícone)"
    elif rarity == "legend" and is_match_worn:
        score = 15
        detail = f"Match worn + lenda → giro rápido (~{liquidez_dias}d)"
    elif rarity == "legend" or liquidez_dias <= 60:
        score = 12
        detail = f"Giro estimado {liquidez_dias}d (lenda)"
    elif rarity == "rare" or liquidez_dias <= 120:
        score = 8
        detail = f"Giro estimado {liquidez_dias}d (raro)"
    else:
        score = 3
        detail = f"Giro lento estimado >{liquidez_dias}d (regional)"

    score = min(score + nba_boost_applied, 15)
    if nba_boost_applied > 0:
        detail += f" | NBA {nba_phase} +{nba_boost_applied}pts"

    return FilterResult("Turnover / Liquidez", score, 15, "VERDE" if score >= 10 else "AMARELO", detail)


# ── F4: Reputacional ──────────────────────────────────────────────────────────

def score_f4_reputational(player_data: dict) -> FilterResult:
    controversies = player_data.get("controversias_ativas", [])
    if controversies:
        return FilterResult("Reputacional", 0, 10, "AMARELO",
                            f"Atenção: {', '.join(controversies[:3])}")
    return FilterResult("Reputacional", 10, 10, "VERDE", "Sem polêmicas ativas conhecidas")


# ── F5: Raridade histórica (do próprio banco) ─────────────────────────────────

def score_f5_rarity(rarity_score: float) -> FilterResult:
    """
    rarity_score: 0–100 (calculado em database/rarity_index.py)
    85+ = nunca visto
    50–84 = esporádico
    25–49 = frequente
    <25 = commodity
    """
    if rarity_score >= 85:
        return FilterResult("Raridade Histórica", 10, 10, "VERDE",
                            f"Item raro — pouquíssimas aparições nos últimos 90d (score {rarity_score:.0f})")
    elif rarity_score >= 50:
        return FilterResult("Raridade Histórica", 7, 10, "VERDE",
                            f"Aparece esporadicamente (score {rarity_score:.0f})")
    elif rarity_score >= 25:
        return FilterResult("Raridade Histórica", 4, 10, "AMARELO",
                            f"Item frequente no mercado (score {rarity_score:.0f})")
    else:
        return FilterResult("Raridade Histórica", 1, 10, "VERMELHO",
                            f"Commodity — aparece muito frequentemente (score {rarity_score:.0f})")


# ── F6: Vendedor ──────────────────────────────────────────────────────────────

def score_f6_seller(listing: dict) -> FilterResult:
    seller = listing.get("seller") or {}
    ratings = seller.get("total_ratings", 0)
    positive_pct = seller.get("positive_pct", 100)

    if ratings >= 50 and positive_pct >= 95:
        return FilterResult("Vendedor", 10, 10, "VERDE",
                            f"{ratings} avaliações, {positive_pct:.0f}% positivas")
    elif ratings >= 10 and positive_pct >= 90:
        return FilterResult("Vendedor", 6, 10, "AMARELO",
                            f"{ratings} avaliações — histórico moderado")
    elif ratings == 0:
        return FilterResult("Vendedor", 0, 10, "VERMELHO", "Vendedor sem histórico")
    else:
        return FilterResult("Vendedor", 3, 10, "AMARELO",
                            f"Histórico limitado: {ratings} avaliações")


# ── F7: Demanda futura (calendário de eventos) ────────────────────────────────

def score_f7_future_demand(player_data: dict) -> FilterResult:
    from config.events_calendar import calculate_event_boost

    boost, reasons = calculate_event_boost(player_data)
    score = min(10 + boost, 25)
    status = "VERDE" if score >= 15 else ("AMARELO" if score >= 8 else "VERMELHO")
    detail = " | ".join(reasons) if reasons else "Sem eventos relevantes próximos"

    return FilterResult("Demanda Futura", score, 25, status, detail)


# ── Engine principal ──────────────────────────────────────────────────────────

def run_score_engine(
    listing: dict,
    sell_price_estimate: float,
    player_data: dict,
    claude_analysis: dict,
    rarity_score: float = 50.0,
    current_stock: dict = None,
) -> ScoreReport:

    flags = check_red_flags(listing)

    if has_critical_flag(flags):
        return ScoreReport(
            listing_id=listing.get("id", ""),
            title=listing.get("title", ""),
            buy_price=listing.get("price", 0),
            sell_price_estimate=sell_price_estimate,
            gross_margin=0.0,
            absolute_profit=0.0,
            filters=[],
            red_flags=flags,
            total_score=0,
            recommendation=Recommendation.REFUSE,
            suggested_offer=None,
            reasoning="Red flag crítico — descarte automático",
        )

    buy_price = listing.get("price", 0)
    margin = calculate_gross_margin(buy_price, sell_price_estimate)
    absolute_profit = sell_price_estimate - buy_price
    penalty = calculate_flag_penalty(flags)

    # Catálogo pessoal: se o item bate com uma JOIA/RARO do estoque, eleva rarity_score
    catalog_match = find_catalog_match(listing.get("title", ""))
    if catalog_match:
        if catalog_match.is_joia:
            rarity_score = max(rarity_score, 80.0)
        elif catalog_match.is_raro:
            rarity_score = max(rarity_score, 65.0)
        else:
            rarity_score = max(rarity_score, 45.0)

    filters = [
        score_f1_margin(margin, buy_price, sell_price_estimate),
        score_f2_authenticity(listing, claude_analysis),
        score_f3_turnover(listing, player_data),
        score_f4_reputational(player_data),
        score_f5_rarity(rarity_score),
        score_f6_seller(listing),
        score_f7_future_demand(player_data),
    ]

    total_score = min(100, max(0, sum(f.score for f in filters) - penalty))

    f2_result = filters[1]
    auth_score_raw = claude_analysis.get("authenticity_score", 50)

    # Suspeita de falsidade (IA) → FLAG AUTENTICADOR
    # Só veta de fato quando o boolean likely_fake/fake_suspicion vem ACOMPANHADO
    # de uma nota de autenticidade baixa. A IA às vezes marca likely_fake=true só
    # porque as fotos disponíveis não mostram claramente o COA/autógrafo (ex: só
    # 1 foto capturada pelo scraper) — isso é incerteza por falta de evidência,
    # não evidência de fraude. Se a própria IA ainda credita ~50/100 de
    # autenticidade, é sinal contraditório/inconclusivo, não suspeita real.
    if (claude_analysis.get("likely_fake") or claude_analysis.get("fake_suspicion")) and auth_score_raw < 40:
        recommendation = Recommendation.FLAG_AUTHENTICATOR
        suggested_offer = None
        reasoning = "IA detectou suspeita de falsidade — verificar com autenticador antes de comprar"

    # Autenticidade REALMENTE baixa (suspeita concreta, não só "não confirmada")
    # — abaixo de 50 já é 0/25 no filtro F2, mas só forçamos o veto quando a IA
    # está de fato desconfiada (<30). Entre 30-49 o item segue no fluxo normal:
    # a nota baixa já puxa o total_score pra baixo sozinha, sem vetar de cara
    # boas oportunidades com margem/raridade/vendedor fortes só por incerteza.
    elif auth_score_raw < 30:
        recommendation = Recommendation.FLAG_AUTHENTICATOR
        suggested_offer = None
        reasoning = f"IA reporta autenticidade muito baixa ({auth_score_raw}/100) — encaminhar para autenticador"

    # Lucro absoluto insuficiente
    elif absolute_profit < MIN_ABSOLUTE_PROFIT:
        recommendation = Recommendation.REFUSE
        suggested_offer = None
        reasoning = (
            f"Lucro absoluto R${absolute_profit:.0f} abaixo do mínimo R${MIN_ABSOLUTE_PROFIT} "
            f"— não vale o esforço operacional"
        )

    # Margem + score ok → COMPRAR
    elif margin >= 0.40 and total_score >= 60:
        recommendation = Recommendation.BUY_NOW
        suggested_offer = None
        catalog_note = ""
        if catalog_match:
            catalog_note = f" | Catálogo: {catalog_match.clube} {catalog_match.periodo} [{catalog_match.tag}]"
        reasoning = (
            f"Margem {margin:.1%} | Lucro R${absolute_profit:.0f} | "
            f"Score {total_score}/100. Oportunidade sólida.{catalog_note}"
        )

    # Margem baixa mas negociável
    elif margin >= 0.20 and total_score >= 40:
        suggested_offer = round(sell_price_estimate * 0.60 / 10) * 10  # arredonda pra dezena
        recommendation = Recommendation.NEGOTIATE
        reasoning = (
            f"Margem atual {margin:.1%} — "
            f"oferecer R${suggested_offer:.0f} para atingir ~40%"
        )

    else:
        recommendation = Recommendation.REFUSE
        suggested_offer = None
        reasoning = (
            f"Margem {margin:.1%} insuficiente ou "
            f"score {total_score}/100 abaixo do mínimo"
        )

    return ScoreReport(
        listing_id=listing.get("id", ""),
        title=listing.get("title", ""),
        buy_price=buy_price,
        sell_price_estimate=sell_price_estimate,
        gross_margin=margin,
        absolute_profit=absolute_profit,
        filters=filters,
        red_flags=flags,
        total_score=total_score,
        recommendation=recommendation,
        suggested_offer=suggested_offer,
        reasoning=reasoning,
    )
