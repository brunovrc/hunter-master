"""
Precificação do Hunter Scout — reaproveita a mesma base de preços do radar
(database/price_tracker.py) para que o valor mostrado em campo seja
consistente com o que o scraper considera "preço de venda" de mercado.

A diferença central em relação ao pipeline de anúncios: aqui não há preço de
compra publicado (o item ainda não está à venda) — o app existe justamente
para SUGERIR quanto oferecer. Por isso a margem exigida é mais conservadora
que a do radar (que já parte de um preço de compra conhecido e barato).
"""
from database.price_tracker import get_sell_price_estimate
from scout.comparables import find_comparables
from scout.schemas import ScoutResult, VisionResult

# Desconto sobre o preço de venda conforme o estado físico da peça.
# A base de preços (FALLBACK_PRICES/catálogo) assume peças em boa/excelente estado.
_CONDITION_MULTIPLIER = {
    "excelente": 1.0,
    "boa": 1.0,
    "regular": 0.75,
    "ruim": 0.50,
}

# Margem mínima exigida na oferta, por faixa de confiança de autenticidade.
# Quanto menor a confiança, maior a margem de segurança exigida.
_MARGIN_HIGH_CONFIDENCE = 0.45    # score >= 80
_MARGIN_MID_CONFIDENCE = 0.55     # score 60-79
_AUTHENTICITY_FLOOR = 60          # abaixo disso: não oferece número, manda verificar

# Faixa de negociação: oferta mínima como % da oferta máxima
_OFFER_RANGE_FLOOR_PCT = 0.65


def _map_item_type(guess: str) -> str:
    """Mapeia o palpite da IA para as chaves usadas em get_sell_price_estimate."""
    if guess in ("autografada", "match_worn", "retro", "player_issue"):
        return guess
    return "retro"  # desconhecido → trata como retro/original genérico (mais conservador)


async def build_scout_result(vision: VisionResult) -> ScoutResult:
    item_type = _map_item_type(vision.item_type_guess)

    # Título sintético só para alimentar heurísticas de preço que esperam texto
    title = f"{vision.player_name} {vision.club} {vision.year_era} {vision.identified_text}".strip()

    sell_price = await get_sell_price_estimate(vision.player_name, item_type, title=title)
    sell_price *= _CONDITION_MULTIPLIER.get(vision.condition, 1.0)

    comparables = await find_comparables(vision.player_name, vision.club)

    # Réplica suspeita ou autenticidade muito baixa → não sugerir compra numérica
    if vision.replica_suspicion or vision.authenticity_score < 30:
        if vision.replica_suspicion:
            reason = (
                "Suspeita de réplica/falsificação — não recomendamos oferecer valor "
                "sem checagem presencial mais detalhada (tecido, costura, etiqueta)."
            )
        else:
            reason = (
                f"Confiança de autenticidade muito baixa ({vision.authenticity_score}/100) — "
                "fotos insuficientes ou inconclusivas para estimar um valor de oferta. "
                "Tire fotos mais nítidas (frente, etiqueta, autógrafo/COA) e avalie de novo."
            )
        return ScoutResult(
            player_name=vision.player_name, club=vision.club, year_era=vision.year_era,
            item_type=item_type, condition=vision.condition,
            is_autographed=vision.is_autographed, is_match_worn=vision.is_match_worn,
            has_coa=vision.has_coa, signature_looks_genuine=vision.signature_looks_genuine,
            replica_suspicion=vision.replica_suspicion, authenticity_score=vision.authenticity_score,
            identified_text=vision.identified_text, ai_notes=vision.notes,
            sell_price_estimate=round(sell_price, 2), offer_min=0, offer_max=0,
            recommendation="VERIFICAR",
            recommendation_reason=reason,
            comparables=comparables,
        )

    if vision.authenticity_score >= 80:
        margin = _MARGIN_HIGH_CONFIDENCE
    else:
        margin = _MARGIN_MID_CONFIDENCE

    offer_max = sell_price * (1 - margin)
    offer_min = offer_max * _OFFER_RANGE_FLOOR_PCT

    if vision.authenticity_score < _AUTHENTICITY_FLOOR:
        recommendation = "VERIFICAR"
        reason = (
            f"Confiança de autenticidade baixa ({vision.authenticity_score}/100) — "
            "peça pode valer a pena, mas recomendamos confirmar com um autenticador "
            "antes de fechar negócio."
        )
    elif vision.condition == "ruim":
        recommendation = "NEGOCIAR"
        reason = "Estado de conservação ruim reduz o valor — negocie abaixo da oferta sugerida."
    else:
        recommendation = "COMPRAR"
        reason = f"Autenticidade e estado consistentes — oferta segura até R${offer_max:,.0f}."

    return ScoutResult(
        player_name=vision.player_name, club=vision.club, year_era=vision.year_era,
        item_type=item_type, condition=vision.condition,
        is_autographed=vision.is_autographed, is_match_worn=vision.is_match_worn,
        has_coa=vision.has_coa, signature_looks_genuine=vision.signature_looks_genuine,
        replica_suspicion=vision.replica_suspicion, authenticity_score=vision.authenticity_score,
        identified_text=vision.identified_text, ai_notes=vision.notes,
        sell_price_estimate=round(sell_price, 2),
        offer_min=round(offer_min, 2), offer_max=round(offer_max, 2),
        recommendation=recommendation, recommendation_reason=reason,
        comparables=comparables,
    )
