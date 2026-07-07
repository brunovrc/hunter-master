"""
Calendário global de eventos com pesos numéricos para F7 (Demanda Futura).

Eventos próximos aumentam o valor de revenda — o mercado antecipa datas.
  < 30 dias: boost máximo (janela de venda)
  30–90 dias: boost alto
  90–180 dias: boost médio
  180–365 dias: boost leve
  > 365 dias: sem boost (muito distante)

Cada evento tem:
  data: date do evento
  boost_base: pontos de boost máximo (aplicado < 30 dias)
  tags: lista de slugs de jogadores ou times que o evento afeta
  descricao: texto legível
"""

from datetime import date, timedelta
from typing import Optional

GLOBAL_EVENTS = [

    # ── COPA DO MUNDO 2026 ────────────────────────────────────────────────────
    {
        "id": "copa_2026",
        "descricao": "Copa do Mundo FIFA 2026 (EUA / Canadá / México)",
        "data": date(2026, 6, 11),
        "boost_base": 25,
        "tags": [
            "brasil", "argentina", "portugal", "franca", "espanha",
            "neymar", "messi", "ronaldo_cr7", "copa_do_mundo",
        ],
        "categoria": "mundial",
    },

    # ── ANIVERSÁRIOS / MARCOS HISTÓRICOS ─────────────────────────────────────
    {
        "id": "maradona_mao_deus_40anos",
        "descricao": "40 anos do 'Gol de Mão de Deus' (Copa 86)",
        "data": date(2026, 6, 22),
        "boost_base": 20,
        "tags": ["maradona", "argentina", "copa86"],
        "categoria": "aniversario",
    },
    {
        "id": "maradona_falecimento_5anos",
        "descricao": "5 anos do falecimento de Maradona",
        "data": date(2025, 11, 25),
        "boost_base": 18,
        "tags": ["maradona", "argentina"],
        "categoria": "memorial",
    },
    {
        "id": "kobe_falecimento_6anos",
        "descricao": "6 anos do falecimento de Kobe Bryant",
        "data": date(2026, 1, 26),
        "boost_base": 20,
        "tags": ["kobe_bryant", "lakers", "nba"],
        "categoria": "memorial",
    },
    {
        "id": "jordan_bulls_titulo_35anos",
        "descricao": "35 anos do primeiro título do Bulls (Jordan, 1991)",
        "data": date(2026, 6, 12),
        "boost_base": 15,
        "tags": ["michael_jordan", "bulls", "pippen"],
        "categoria": "aniversario",
    },
    {
        "id": "pele_cosmos_despedida_50anos",
        "descricao": "50 anos da despedida de Pelé (Cosmos x Santos, 01/10/1977)",
        "data": date(2027, 10, 1),
        "boost_base": 30,
        "tags": ["pele", "cosmos", "santos", "icon"],
        "categoria": "aniversario",
    },
    {
        "id": "brasil_copa94_30anos",
        "descricao": "30 anos da Copa do Mundo 1994 (Romário, Bebeto)",
        "data": date(2024, 7, 17),
        "boost_base": 12,
        "tags": ["romario", "bebeto", "cafu", "brasil", "copa94"],
        "categoria": "aniversario",
    },
    {
        "id": "copa_america_2024",
        "descricao": "Copa América 2024 (EUA)",
        "data": date(2024, 6, 20),
        "boost_base": 15,
        "tags": ["messi", "neymar", "argentina", "brasil"],
        "categoria": "torneio",
    },
    {
        "id": "copa_america_2028",
        "descricao": "Copa América 2028",
        "data": date(2028, 6, 1),
        "boost_base": 10,
        "tags": ["messi", "argentina", "brasil"],
        "categoria": "torneio",
    },

    # ── NBA EVENTS ────────────────────────────────────────────────────────────
    {
        "id": "nba_playoffs_2026",
        "descricao": "NBA Playoffs 2026",
        "data": date(2026, 4, 18),
        "boost_base": 20,
        "tags": ["lebron_james", "stephen_curry", "nba", "basketball"],
        "categoria": "torneio",
    },
    {
        "id": "nba_finals_2026",
        "descricao": "NBA Finals 2026",
        "data": date(2026, 6, 4),
        "boost_base": 35,
        "tags": ["lebron_james", "stephen_curry", "nba", "basketball"],
        "categoria": "torneio",
    },
    {
        "id": "nba_hof_2026",
        "descricao": "NBA Hall of Fame 2026 (indução)",
        "data": date(2026, 9, 12),
        "boost_base": 15,
        "tags": ["nba", "basketball"],
        "categoria": "premiacao",
    },
    {
        "id": "basquete_mundial_2026",
        "descricao": "Copa do Mundo de Basquete 2026",
        "data": date(2026, 8, 1),
        "boost_base": 20,
        "tags": ["lebron_james", "stephen_curry", "nba", "basketball", "eua"],
        "categoria": "mundial",
    },

    # ── LEILÕES IMPORTANTES ───────────────────────────────────────────────────
    {
        "id": "goldin_spring_2026",
        "descricao": "Goldin Auctions Spring Premier 2026",
        "data": date(2026, 4, 1),
        "boost_base": 10,
        "tags": ["nba", "football", "colecao"],
        "categoria": "leilao",
    },
    {
        "id": "heritage_sports_2026",
        "descricao": "Heritage Sports Collectibles Signature Auction 2026",
        "data": date(2026, 5, 1),
        "boost_base": 10,
        "tags": ["nba", "football", "colecao"],
        "categoria": "leilao",
    },

]


def calculate_event_boost(player_data: dict, listing_tags: list = None) -> tuple[int, list[str]]:
    """
    Calcula boost total de F7 baseado em eventos próximos relevantes ao atleta.
    Retorna (boost_total, lista_de_razoes).
    Dedup por event_id para evitar triple-counting do mesmo evento.
    """
    today = date.today()
    total_boost = 0
    reasons = []
    counted_ids: set = set()

    player_tags = set(player_data.get("tags", []))
    if listing_tags:
        player_tags.update(listing_tags)

    # Boost da Copa 2026 via flag dedicado (fonte primária)
    if player_data.get("copa_2026"):
        counted_ids.add("copa_2026")  # marca para não contar de novo
        days_to_copa = (date(2026, 6, 11) - today).days
        if 0 <= days_to_copa <= 365:
            copa_boost = _time_decay_boost(25, days_to_copa)
            if copa_boost > 0:
                total_boost += copa_boost
                reasons.append(f"Copa 2026 em {days_to_copa}d (+{copa_boost})")

    # Eventos específicos do player_data (usa descricao como ID)
    for event in player_data.get("eventos_futuros", []):
        event_date = event.get("data")
        if not event_date:
            continue
        # Pula se já contamos Copa 2026 via flag
        descr = event.get("descricao", "")
        if "copa" in descr.lower() and "2026" in descr and "copa_2026" in counted_ids:
            continue
        days = (event_date - today).days
        if -30 <= days <= 365:
            boost = _time_decay_boost(event.get("boost", 5), max(days, 0))
            if boost > 0:
                total_boost += boost
                reasons.append(f"{descr} ({'+' if days >= 0 else ''}{days}d, +{boost})")

    # Calendário global — pula eventos já contados
    for event in GLOBAL_EVENTS:
        event_id = event.get("id", "")
        if event_id in counted_ids:
            continue

        event_tags = set(event.get("tags", []))
        if not event_tags.intersection(player_tags):
            continue

        days = (event["data"] - today).days
        if -30 <= days <= 365:
            boost = _time_decay_boost(event["boost_base"], max(days, 0))
            if boost > 0:
                total_boost += boost
                counted_ids.add(event_id)
                reasons.append(f"{event['descricao']} ({days}d, +{boost})")

    return min(total_boost, 40), reasons  # cap em 40 pts para F7


def _time_decay_boost(base: int, days_until: int) -> int:
    """Decai o boost conforme a distância temporal do evento."""
    if days_until <= 30:
        return base
    elif days_until <= 90:
        return int(base * 0.75)
    elif days_until <= 180:
        return int(base * 0.50)
    elif days_until <= 365:
        return int(base * 0.25)
    return 0


def get_upcoming_events(days_ahead: int = 90) -> list[dict]:
    """Retorna eventos nos próximos N dias (útil para relatório diário)."""
    today = date.today()
    cutoff = today + timedelta(days=days_ahead)
    return [
        e for e in GLOBAL_EVENTS
        if today <= e["data"] <= cutoff
    ]
