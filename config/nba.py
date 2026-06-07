"""
Camada NBA — banco de atletas, taxonomia, sazonalidade e preços de referência.

Sazonalidade NBA:
  Out–Abr: temporada regular → demanda estável
  Abr–Jun: playoffs → pico de demanda (+20–40%)
  Jun–Jul: Finals → pico máximo (+50%)
  Jul–Set: offseason → demanda base
  Indução ao Hall of Fame (Set): boost pontual em veteranos
"""

from datetime import date

NBA_PLAYERS = {

    # ── ÍCONES ABSOLUTOS ──────────────────────────────────────────────────────

    "michael_jordan": {
        "nomes_busca": [
            "Michael Jordan", "MJ", "Air Jordan", "His Airness",
            "Jordan Bulls", "Jordan Chicago",
        ],
        "times": ["Chicago Bulls", "Washington Wizards", "EUA"],
        "raridade": "icon",
        "liquidez_dias": 10,
        "preco_referencia": {
            "autografado": 15000,
            "match_worn": 50000,
            "retro": 3000,
            "player_edition": 8000,
        },
        "sazonalidade_boost": {"playoffs": 30, "finals": 50, "offseason": 0},
        "eventos_futuros": [
            {"descricao": "35 anos título Bulls 1991", "data": date(2026, 6, 12), "boost": 15},
        ],
        "tags": ["bulls", "chicago", "air_jordan", "seis_titulos", "mvp"],
    },

    "kobe_bryant": {
        "nomes_busca": [
            "Kobe Bryant", "Kobe", "Black Mamba", "Bean Bryant",
            "Kobe Lakers",
        ],
        "times": ["Los Angeles Lakers", "EUA"],
        "raridade": "icon",
        "liquidez_dias": 10,
        "preco_referencia": {
            "autografado": 12000,
            "match_worn": 40000,
            "retro": 2500,
            "player_edition": 7000,
        },
        "sazonalidade_boost": {"playoffs": 25, "finals": 40, "offseason": 5},
        "eventos_futuros": [
            {"descricao": "6 anos do falecimento", "data": date(2026, 1, 26), "boost": 20},
        ],
        "tags": ["lakers", "black_mamba", "cinco_titulos", "mvp"],
    },

    # ── LENDAS NBA ────────────────────────────────────────────────────────────

    "lebron_james": {
        "nomes_busca": ["LeBron James", "LeBron", "King James", "The King", "LBJ"],
        "times": ["Cleveland Cavaliers", "Miami Heat", "Los Angeles Lakers", "EUA"],
        "raridade": "icon",
        "liquidez_dias": 12,
        "preco_referencia": {
            "autografado": 8000,
            "match_worn": 30000,
            "retro": 2000,
            "player_edition": 5000,
        },
        "sazonalidade_boost": {"playoffs": 35, "finals": 55, "offseason": 0},
        "eventos_futuros": [
            {"descricao": "Copa do Mundo de Basquete 2026", "data": date(2026, 8, 1), "boost": 15},
        ],
        "tags": ["lakers", "heat", "cavaliers", "king_james"],
    },

    "magic_johnson": {
        "nomes_busca": ["Magic Johnson", "Magic", "Earvin Johnson"],
        "times": ["Los Angeles Lakers", "EUA"],
        "raridade": "legend",
        "liquidez_dias": 30,
        "preco_referencia": {
            "autografado": 3000,
            "match_worn": 12000,
            "retro": 800,
            "player_edition": 2000,
        },
        "sazonalidade_boost": {"playoffs": 15, "finals": 25, "offseason": 0},
        "eventos_futuros": [],
        "tags": ["lakers", "showtime", "cinco_titulos"],
    },

    "larry_bird": {
        "nomes_busca": ["Larry Bird", "Bird", "Larry Legend"],
        "times": ["Boston Celtics", "EUA"],
        "raridade": "legend",
        "liquidez_dias": 35,
        "preco_referencia": {
            "autografado": 2500,
            "match_worn": 10000,
            "retro": 700,
            "player_edition": 1800,
        },
        "sazonalidade_boost": {"playoffs": 12, "finals": 20, "offseason": 0},
        "eventos_futuros": [],
        "tags": ["celtics", "tres_titulos", "larry_legend"],
    },

    "shaquille_oneal": {
        "nomes_busca": ["Shaquille O'Neal", "Shaq", "Shaquille", "Shaq Diesel", "The Big Aristotle"],
        "times": ["Orlando Magic", "Los Angeles Lakers", "Miami Heat", "EUA"],
        "raridade": "legend",
        "liquidez_dias": 40,
        "preco_referencia": {
            "autografado": 2500,
            "match_worn": 9000,
            "retro": 700,
            "player_edition": 1800,
        },
        "sazonalidade_boost": {"playoffs": 15, "finals": 25, "offseason": 0},
        "eventos_futuros": [],
        "tags": ["lakers", "heat", "quatro_titulos"],
    },

    "stephen_curry": {
        "nomes_busca": ["Stephen Curry", "Steph Curry", "Chef Curry", "Wardell Curry"],
        "times": ["Golden State Warriors", "EUA"],
        "raridade": "rare",
        "liquidez_dias": 50,
        "preco_referencia": {
            "autografado": 3000,
            "match_worn": 12000,
            "retro": 800,
            "player_edition": 2000,
        },
        "sazonalidade_boost": {"playoffs": 30, "finals": 45, "offseason": 5},
        "eventos_futuros": [
            {"descricao": "Copa do Mundo de Basquete 2026", "data": date(2026, 8, 1), "boost": 20},
        ],
        "tags": ["warriors", "splash_brothers", "quatro_titulos"],
    },

    "scottie_pippen": {
        "nomes_busca": ["Scottie Pippen", "Pippen", "Pip"],
        "times": ["Chicago Bulls", "EUA"],
        "raridade": "legend",
        "liquidez_dias": 50,
        "preco_referencia": {
            "autografado": 1500,
            "match_worn": 5000,
            "retro": 500,
            "player_edition": 1200,
        },
        "sazonalidade_boost": {"playoffs": 10, "finals": 15, "offseason": 0},
        "eventos_futuros": [],
        "tags": ["bulls", "chicago", "six_rings", "dupla_jordan"],
    },

    "dennis_rodman": {
        "nomes_busca": ["Dennis Rodman", "Rodman", "The Worm"],
        "times": ["Detroit Pistons", "Chicago Bulls", "San Antonio Spurs", "EUA"],
        "raridade": "rare",
        "liquidez_dias": 60,
        "preco_referencia": {
            "autografado": 1500,
            "match_worn": 4500,
            "retro": 450,
            "player_edition": 1200,
        },
        "sazonalidade_boost": {"playoffs": 8, "finals": 12, "offseason": 0},
        "eventos_futuros": [],
        "tags": ["bulls", "pistons", "worm"],
    },

    "charles_barkley": {
        "nomes_busca": ["Charles Barkley", "Barkley", "Sir Charles", "The Round Mound of Rebound"],
        "times": ["Philadelphia 76ers", "Phoenix Suns", "Houston Rockets", "EUA"],
        "raridade": "legend",
        "liquidez_dias": 55,
        "preco_referencia": {
            "autografado": 1800,
            "match_worn": 6000,
            "retro": 500,
            "player_edition": 1400,
        },
        "sazonalidade_boost": {"playoffs": 10, "finals": 18, "offseason": 0},
        "eventos_futuros": [],
        "tags": ["suns", "76ers", "mvp"],
    },

    "allen_iverson": {
        "nomes_busca": ["Allen Iverson", "Iverson", "AI", "The Answer"],
        "times": ["Philadelphia 76ers", "EUA"],
        "raridade": "legend",
        "liquidez_dias": 40,
        "preco_referencia": {
            "autografado": 2000,
            "match_worn": 7000,
            "retro": 600,
            "player_edition": 1500,
        },
        "sazonalidade_boost": {"playoffs": 15, "finals": 20, "offseason": 5},
        "eventos_futuros": [],
        "tags": ["76ers", "the_answer", "mvp", "crossover"],
    },

}

# ── SAZONALIDADE ATUAL ─────────────────────────────────────────────────────────

def get_nba_season_boost() -> tuple[str, int]:
    """
    Retorna (fase_atual, boost_percentual) baseado na data.
    Playoffs NBA: ~Abr–Jun | Finals: ~Jun–Jul | Draft: Jul | Pré-temporada: Set
    """
    today = date.today()
    month = today.month

    if month in (6, 7):
        return ("finals", 50)
    elif month in (4, 5):
        return ("playoffs", 30)
    elif month == 9:
        return ("hall_of_fame", 10)
    elif month in (10, 11, 12, 1, 2, 3):
        return ("regular_season", 10)
    else:
        return ("offseason", 0)


def find_nba_player(title: str, extracted_name: str = "") -> dict | None:
    search_text = f"{title} {extracted_name}".lower()
    for key, data in NBA_PLAYERS.items():
        for name in data.get("nomes_busca", []):
            if name.lower() in search_text:
                return data
    return None
