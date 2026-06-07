"""
Dicionário centralizado de termos de busca por segmento.
Todos os scrapers importam daqui — nunca hardcodar queries em scraper individual.
"""

# ── FUTEBOL BR ─────────────────────────────────────────────────────────────────

FOOTBALL_BR = [
    # Genérico autógrafo — captura qualquer camisa autografada
    "camisa futebol autografada",
    "camisa futebol autografo",
    "camisa futebol assinada jogador",
    "camisa futebol match worn",
    "camisa autografada COA",
    "camisa autografada PSA",
    "camisa autografada Beckett",
    # Retro / vintage / joia — sem player-específico (ML filtra por título depois)
    "camisa futebol vintage original",
    "camisa futebol retro original",
    "camisa copa do mundo original",
    "camisa brasil original",
    "camisa libertadores original",
    "camisa futebol joia colecionador",
    # Player issue
    "camisa futebol player issue",
    "camisa futebol edição limitada numerada",
]

# ── FUTEBOL AR ─────────────────────────────────────────────────────────────────

FOOTBALL_AR = [
    "camiseta futbol autografiada",
    "camiseta futbol firmada jugador",
    "camiseta futbol match worn",
    "camiseta futbol autografiada COA",
    "camiseta futbol autografiada PSA",
    "camiseta futbol vintage original",
    "camiseta futbol retro original",
    "camiseta futbol player issue",
]

# ── BASQUETE (BR + AR) ─────────────────────────────────────────────────────────

BASKETBALL = [
    "camisa nba autografada",
    "jersey nba autografado",
    "camisa basquete autografada",
    "camisa nba match worn",
    "jersey nba player edition",
]

# ── ENJOEI (subset otimizado) ──────────────────────────────────────────────────

ENJOEI_BR = [
    # Genérico — captura qualquer autógrafo real
    "camisa futebol autografada",
    "camisa futebol match worn",
    "camisa futebol autografada certificado",
    # Lendas absolutas — maior liquidez e ticket
    "pele autografado",
    "maradona autografado",
    "zico autografado",
    "ronaldo fenomeno autografado",
    "ronaldinho autografado",
    "neymar autografado camisa",
    # NBA
    "camisa nba autografada",
    "jordan autografado",
    # Vintage / retro original
    "camisa copa do mundo original",
]

# ── FILTROS NEGATIVOS ──────────────────────────────────────────────────────────

NEGATIVE_TITLE_TERMS = [
    "réplica", "replica",
    "tailandesa", "tailandês", "tailandes",
    "imitação", "imitacao", "imitacion",
    "cópia", "copia",
    "fake", "falsificad",
    "inspirada", "inspirado",
    "temática", "tematica",
    "similar ao original",
    "fanática", "fanatica",
    "não autografad",
    "sem autografo", "sem autógrafo",
    "comemorativa", "homenagem",
    "coleção torcedor", "camisa torcedor",
    "edição torcedor",
    "kit com ", "lote de ", "pacote com ",
    "10 unidades", "5 unidades",
    "coloque seu nome", "personalize", "nome a escolher",
    "nome personalizado",
    "retrômania", "retromania", "retro mania",
    "super bolla",
    "lacoste", "osklen",
    "baby look", "blusa feminina", "polo brasil", "camisa polo",
    "camiseta estonada", "100% algodão", "100% algodao",
    "kit 4 camisas", "kit 3 camisas", "kit 2 camisas",
    "torcedor oficial",
]

# ── PISOS DE PREÇO ─────────────────────────────────────────────────────────────

PRICE_FLOOR = {
    "default":      100,
    "autografada":  500,
    "match_worn":   800,
    "coa_psa":      600,
    "coa_beckett":  700,
    "player_issue": 400,
    "nba":          300,
    "lenda_icone": 1500,
    "lenda_top":    800,
    "lenda_media":  500,
}

_ICON_TERMS = [
    "pelé", "pele", "maradona", "michael jordan", "kobe bryant",
    "garrincha",
]

_TOP_LEGEND_TERMS = [
    "zico", "ronaldo fenomeno", "ronaldo r9", " r9 ",
    "messi", "cristiano ronaldo", " cr7 ",
    "ronaldinho", " r10 ", "ronaldinho gaucho",
    "kobe", "lebron", "magic johnson", "larry bird",
    "maradona", "beckham", "zidane",
    "romario", "rivaldo", "kempes", "batistuta",
    "carlos alberto torres", "tostao", "jairzinho",
]

_MID_LEGEND_TERMS = [
    "kaka", "kaká", "neymar", "cafu", "roberto carlos",
    "thiago silva", "daniel alves", "casemiro", "hulk", "gabigol",
    "totti", "maldini", "del piero", "buffon",
    "iniesta", "xavi", "gerrard", "rooney", "henry", "drogba",
    "shaquille", "shaq", "curry", "stephen curry", "allen iverson",
    "charles barkley", "kevin durant", "scottie pippen", "dennis rodman",
    "dunga", "socrates", "bebeto", "rivelino",
    "riquelme", "caniggia", "tevez", "zanetti", "aguero",
    "mbappe", "haaland", "vinicius", "vini jr",
]

PRICE_CEILING = {
    "football_generic": 25000,
    "nba":              60000,
    "icon":            200000,
}


def get_price_floor(listing: dict) -> float:
    title = (listing.get("title") or "").lower()
    has_autograph = any(t in title for t in ["autograf", "assinad", "firmad", "autografiada"])

    if has_autograph and any(t in title for t in _ICON_TERMS):
        return PRICE_FLOOR["lenda_icone"]

    if has_autograph and any(t in title for t in _TOP_LEGEND_TERMS):
        return PRICE_FLOOR["lenda_top"]

    if any(t in title for t in ["match worn", "usada em jogo", "usada en partido"]):
        return PRICE_FLOOR["match_worn"]

    if "psa" in title or "beckett" in title:
        return PRICE_FLOOR["coa_beckett"]

    if "coa" in title or "certificado" in title:
        return PRICE_FLOOR["coa_psa"]

    if has_autograph and any(t in title for t in _MID_LEGEND_TERMS):
        return PRICE_FLOOR["lenda_media"]

    if has_autograph:
        return PRICE_FLOOR["autografada"]

    if "player issue" in title or "player edition" in title:
        return PRICE_FLOOR["player_issue"]

    if "nba" in title or "basquete" in title or "basquet" in title:
        return PRICE_FLOOR["nba"]

    return PRICE_FLOOR["default"]
