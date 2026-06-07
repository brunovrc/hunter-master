"""
Dicionário centralizado de termos de busca por segmento.
Todos os scrapers importam daqui — nunca hardcodar queries em scraper individual.
"""

# ── FUTEBOL BR ─────────────────────────────────────────────────────────────────

FOOTBALL_BR = [
    # ── Autografado genérico — máxima prioridade
    "camisa futebol autografada",
    "camisa futebol autografo",
    "camisa futebol assinada jogador",
    "camisa futebol match worn",
    "camisa futebol usada em jogo",
    "camisa futebol autografada COA",
    "camisa futebol autografada PSA",
    "camisa futebol autografada Beckett",
    "camisa futebol autografada certificado autenticidade",
    # ── Lendas brasileiras
    "pele autografado camisa",
    "zico autografado camisa",
    "ronaldo fenomeno autografado camisa",
    "romario autografado camisa",
    "socrates autografado camisa",
    "neymar autografado camisa",
    "ronaldinho autografado camisa",
    "rivaldo autografado camisa",
    "kaka autografado camisa",
    "adriano autografado camisa",
    "bebeto autografado camisa",
    "cafu autografado camisa",
    "roberto carlos autografado camisa",
    "vinicius jr autografado camisa",
    "gabriel martinelli autografado camisa",
    "dunga autografado camisa",
    # ── Lendas argentinas / mundiais (vendidos BR)
    "maradona autografado camisa",
    "messi autografado camisa",
    "beckham autografado camisa",
    "zidane autografado camisa",
    "henry autografado camisa",
    "totti autografado camisa",
    "maldini autografado camisa",
    "del piero autografado camisa",
    "baggio autografado camisa",
    "cannavaro autografado camisa",
    "shevchenko autografado camisa",
    "van basten autografado camisa",
    "gullit autografado camisa",
    "figo autografado camisa",
    "iniesta autografado camisa",
    "xavi autografado camisa",
    "gerrard autografado camisa",
    "rooney autografado camisa",
    "suarez autografado camisa",
    "drogba autografado camisa",
    "ballack autografado camisa",
    "batistuta autografado camisa",
    "riquelme autografado camisa",
    "aguero autografado camisa",
    "higuita autografado camisa",
    "bale autografado camisa",
    "ronaldo cr7 autografado camisa",
    # ── Player issue / edição especial
    "camisa futebol player issue",
    "camisa futebol player edition",
    "camisa futebol edição limitada numerada",
    "camisa futebol versão jogador",
    # ── Vintage / retro / Joia (camisas originais de épocas icônicas)
    "camisa futebol vintage original",
    "camisa futebol retro original",
    "camisa copa do mundo original",
    "camisa brasil 2002 original",
    "camisa brasil 1998 original",
    "camisa libertadores original",
    "camisa champions league original",
    "camisa joia colecionador",
    "camisa futebol original anos 90",
    "camisa futebol original anos 2000",
]

# ── FUTEBOL AR ─────────────────────────────────────────────────────────────────

FOOTBALL_AR = [
    # ── Autografado genérico (espanhol)
    "camiseta futbol autografiada",
    "camiseta futbol firmada jugador",
    "camiseta futbol match worn",
    "camiseta futbol autografiada COA",
    "camiseta futbol autografiada certificado autenticidad",
    "camiseta futbol autografiada PSA",
    "camiseta futbol autografiada Beckett",
    # ── Lendas argentinas
    "maradona camiseta autografiada",
    "messi camiseta autografiada",
    "kempes camiseta autografiada",
    "batistuta camiseta autografiada",
    "riquelme camiseta autografiada",
    "caniggia camiseta autografiada",
    "tevez camiseta autografiada",
    "zanetti camiseta autografiada",
    "aguero camiseta autografiada",
    "di maria camiseta autografiada",
    "crespo camiseta autografiada",
    "mascherano camiseta autografiada",
    "veron camiseta autografiada",
    "higuain camiseta autografiada",
    "lautaro martinez camiseta autografiada",
    # ── Lendas mundiais (vendidos no AR)
    "beckham camiseta autografiada",
    "ronaldinho camiseta autografiada",
    "zidane camiseta autografiada",
    "ronaldo nazario camiseta autografiada",
    "totti camiseta autografiada",
    "del piero camiseta autografiada",
    "maldini camiseta autografiada",
    "figo camiseta autografiada",
    "henry camiseta autografiada",
    "iniesta camiseta autografiada",
    # ── Player issue
    "camiseta futbol player issue",
    "camiseta futbol edicion limitada numerada",
]

# ── BASQUETE (BR + AR) ─────────────────────────────────────────────────────────

BASKETBALL = [
    # ── Genérico NBA (jersey obrigatório nas queries)
    "camisa nba autografada",
    "jersey nba autografado",
    "camiseta nba autografiada",
    "camisa basquete autografada",
    "camiseta basquet autografiada",
    # ── Ícones NBA
    "michael jordan camisa autografada",
    "jordan bulls camisa autografada",
    "kobe bryant camisa autografada",
    "kobe lakers camisa autografada",
    "lebron james camisa autografada",
    # ── Lendas NBA
    "magic johnson camisa autografada",
    "larry bird camisa autografada",
    "shaquille oneal camisa autografada",
    "stephen curry camisa autografada",
    "allen iverson camisa autografada",
    "charles barkley camisa autografada",
    "scottie pippen camisa autografada",
    "dennis rodman camisa autografada",
    "kevin durant camisa autografada",
    "dwyane wade camisa autografada",
    "dirk nowitzki camisa autografada",
    "tim duncan camisa autografada",
    "karl malone camisa autografada",
    # ── Player editions
    "camisa nba match worn",
    "jersey nba player edition",
    "camisa nba edição especial",
    "jersey nba game issued",
]

# ── ENJOEI (subset — menos queries, foco no que funciona) ──────────────────────

ENJOEI_BR = [
    "camisa futebol autografada",
    "camisa futebol autografo",
    "camisa futebol assinada jogador",
    "camisa futebol match worn",
    "camisa futebol autografada certificado",
    "pele autografado",
    "zico autografado",
    "ronaldo fenomeno autografado",
    "neymar autografado camisa",
    "romario autografado",
    "maradona autografado",
    "messi autografado camisa",
    "camisa futebol player issue",
    "camisa nba autografada",
    "jordan autografado",
    "kobe autografado",
    # ── Vintage / retro — Enjoei é forte nisso
    "camisa futebol vintage original",
    "camisa futebol retro original",
    "camisa copa do mundo original",
    "camisa libertadores original",
    "camisa joia colecionador",
    "camisa futebol original rara",
]

# ── FILTROS NEGATIVOS ──────────────────────────────────────────────────────────
# Presença de qualquer um desses no título = rejeição imediata sem análise AI

NEGATIVE_TITLE_TERMS = [
    # Produto explicitamente falso / réplica
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
    # Camisas comemorativas / homenagem — estampam "autógrafo" mas não são reais
    "comemorativa", "homenagem",
    "coleção torcedor", "camisa torcedor",
    "edição torcedor",
    # Termos que indicam produto em série (não item único)
    "kit com ", "lote de ", "pacote com ",
    "10 unidades", "5 unidades",
    # Personalizadas explicitamente
    "coloque seu nome", "personalize", "nome a escolher",
    "nome personalizado",
    # Marcas de retro licenciado — produtos em série
    "retrômania", "retromania", "retro mania",
    "super bolla",
    # Marcas de moda — não são camisas esportivas de colecionador
    "lacoste", "osklen",
    # Peças de roupa que não são jersey esportivo
    "baby look", "blusa feminina", "polo brasil", "camisa polo",
    "camiseta estonada", "100% algodão", "100% algodao",
    # Packs de merchan — não é item único
    "kit 4 camisas", "kit 3 camisas", "kit 2 camisas",
    # Torcedor de temporada atual (não colecionador)
    "torcedor oficial",
]

# ── PISOS DE PREÇO POR CATEGORIA ───────────────────────────────────────────────
# Abaixo desse valor, rejeita sem análise AI (muito barato pra ser item real)

PRICE_FLOOR = {
    "default":          100,
    "autografada":      500,   # autógrafo real mínimo realista — R$250 era irreal
    "match_worn":       800,   # match worn barato é suspeito
    "coa_psa":          600,
    "coa_beckett":      700,
    "player_issue":     400,
    "nba":              300,
    "lenda_icone":     1500,   # Pelé, Maradona, Jordan — abaixo disso é quase certamente falso
    "lenda_top":        800,   # Zico, Ronaldo, Messi, CR7, Kobe, LeBron
    "lenda_media":      500,   # demais lendas reconhecidas
}

# Lendas absolutas — piso altíssimo (autógrafo desses por menos de R$1500 não existe)
_ICON_TERMS = [
    "pelé", "pele", "maradona", "michael jordan", "kobe bryant",
]

# Lendas top — autógrafo real abaixo de R$800 é muito suspeito
_TOP_LEGEND_TERMS = [
    "zico", "ronaldo fenomeno", "ronaldo r9", " r9 ",
    "messi", "cristiano ronaldo", " cr7 ",
    "ronaldinho", " r10 ", "ronaldinho gaucho",
    "kobe", "lebron", "magic johnson", "larry bird",
    "maradona", "beckham", "zidane",
]

# Lendas médias — piso de R$500
_MID_LEGEND_TERMS = [
    "romario", "rivaldo", "kaka", "kaká", "neymar", "cafu", "roberto carlos",
    "batistuta", "totti", "maldini", "del piero", "buffon",
    "iniesta", "xavi", "gerrard", "rooney", "henry", "drogba",
    "shaquille", "shaq", "curry", "stephen curry", "allen iverson", "iverson",
    "charles barkley", "barkley", "kevin durant", "durant",
    "scottie pippen", "pippen", "dennis rodman", "rodman",
]

# Tetos de preço — acima desses, flag para verificação extra (não rejeita)
PRICE_CEILING = {
    "football_generic": 25000,
    "nba":              60000,
    "icon":            200000,
}


def get_price_floor(listing: dict) -> float:
    """Retorna o piso de preço adequado para o item baseado em seu título."""
    title = (listing.get("title") or "").lower()
    has_autograph = any(t in title for t in ["autograf", "assinad", "firmad", "autografiada"])

    # Ícones absolutos — autógrafo por menos de R$1500 é quase certamente falso
    if has_autograph and any(t in title for t in _ICON_TERMS):
        return PRICE_FLOOR["lenda_icone"]

    # Lendas top — piso de R$800
    if has_autograph and any(t in title for t in _TOP_LEGEND_TERMS):
        return PRICE_FLOOR["lenda_top"]

    if any(t in title for t in ["match worn", "usada em jogo", "usada en partido"]):
        return PRICE_FLOOR["match_worn"]

    if "psa" in title or "beckett" in title:
        return PRICE_FLOOR["coa_beckett"]

    if "coa" in title or "certificado" in title:
        return PRICE_FLOOR["coa_psa"]

    # Lendas médias — piso de R$500
    if has_autograph and any(t in title for t in _MID_LEGEND_TERMS):
        return PRICE_FLOOR["lenda_media"]

    if has_autograph:
        return PRICE_FLOOR["autografada"]

    if "player issue" in title or "player edition" in title:
        return PRICE_FLOOR["player_issue"]

    if "nba" in title or "basquete" in title or "basquet" in title:
        return PRICE_FLOOR["nba"]

    return PRICE_FLOOR["default"]
