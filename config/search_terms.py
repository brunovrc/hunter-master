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

    # ── Heróis Copa 1958 / 1962
    "pele autografado camisa",
    "garrincha autografado camisa",
    "didi autografado camisa",
    "zagallo autografado camisa",
    "vava autografado camisa",
    "nilton santos autografado camisa",
    "amarildo autografado camisa",

    # ── Heróis Copa 1970
    "tostao autografado camisa",
    "rivelino autografado camisa",
    "jairzinho autografado camisa",
    "gerson autografado camisa",
    "carlos alberto torres autografado camisa",
    "clodoaldo autografado camisa",
    "taffarel autografado camisa",

    # ── Heróis Copa 1994
    "romario autografado camisa",
    "bebeto autografado camisa",
    "mazenga autografado camisa",
    "cafu autografado camisa",
    "leonardo autografado camisa",
    "mazinho autografado camisa",
    "aldair autografado camisa",
    "marcio santos autografado camisa",
    "branco autografado camisa",
    "rai autografado camisa",

    # ── Heróis Copa 2002
    "ronaldo fenomeno autografado camisa",
    "ronaldinho autografado camisa",
    "rivaldo autografado camisa",
    "roberto carlos autografado camisa",
    "kleberson autografado camisa",
    "edmilson autografado camisa",
    "gilberto silva autografado camisa",
    "lucio autografado camisa",
    "marcos autografado camisa",
    "denilson autografado camisa",

    # ── Lendas gerais BR
    "socrates autografado camisa",
    "zico autografado camisa",
    "dunga autografado camisa",
    "kaka autografado camisa",
    "adriano autografado camisa",
    "ronaldao autografado camisa",
    "cesar sampaio autografado camisa",
    "juninho pernambucano autografado camisa",
    "elano autografado camisa",
    "alexandre pato autografado camisa",
    "oscar autografado camisa",
    "hulk autografado camisa",
    "fred autografado camisa",
    "david luiz autografado camisa",
    "thiago silva autografado camisa",
    "daniel alves autografado camisa",
    "casemiro autografado camisa",
    "philippe coutinho autografado camisa",
    "gabriel jesus autografado camisa",
    "firmino autografado camisa",
    "neymar autografado camisa",
    "vinicius jr autografado camisa",
    "rodrygo autografado camisa",
    "gabriel martinelli autografado camisa",
    "endrick autografado camisa",
    "gabigol autografado camisa",

    # ── Campeões Libertadores — times históricos
    "camisa flamengo libertadores autografada",
    "camisa santos libertadores autografada",
    "camisa gremio libertadores autografada",
    "camisa sao paulo libertadores autografada",
    "camisa cruzeiro libertadores autografada",
    "camisa atletico mineiro libertadores autografada",
    "camisa internacional libertadores autografada",
    "camisa fluminense libertadores autografada",
    "camisa estudiantes autografada",

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
    "caniggia autografado camisa",
    "ortega autografado camisa",
    "kempes autografado camisa",
    "higuita autografado camisa",
    "bale autografado camisa",
    "ronaldo cr7 autografado camisa",
    "mbappe autografado camisa",
    "haaland autografado camisa",
    "benzema autografado camisa",
    "modric autografado camisa",
    "cavani autografado camisa",
    "di maria autografado camisa",

    # ── Player issue / edição especial
    "camisa futebol player issue",
    "camisa futebol player edition",
    "camisa futebol edição limitada numerada",
    "camisa futebol versão jogador",

    # ── Vintage / retro / Joia
    "camisa futebol vintage original",
    "camisa futebol retro original",
    "camisa copa do mundo original",
    "camisa brasil 2002 original",
    "camisa brasil 1998 original",
    "camisa brasil 1994 original",
    "camisa brasil 1970 original",
    "camisa libertadores original",
    "camisa champions league original",
    "camisa joia colecionador",
    "camisa futebol original anos 90",
    "camisa futebol original anos 80",
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

    # ── Campeões mundiais Argentina 1978 / 1986 / 2022
    "maradona camiseta autografiada",
    "kempes camiseta autografiada",
    "ardiles camiseta autografiada",
    "passarella camiseta autografiada",
    "tapia autografiada",
    "burruchaga camiseta autografiada",
    "valdano camiseta autografiada",
    "caniggia camiseta autografiada",
    "messi camiseta autografiada",
    "di maria camiseta autografiada",
    "otamendi camiseta autografiada",
    "de paul camiseta autografiada",
    "lautaro martinez camiseta autografiada",
    "martinez emi camiseta autografiada",

    # ── Outras lendas AR
    "batistuta camiseta autografiada",
    "riquelme camiseta autografiada",
    "tevez camiseta autografiada",
    "zanetti camiseta autografiada",
    "aguero camiseta autografiada",
    "crespo camiseta autografiada",
    "mascherano camiseta autografiada",
    "veron camiseta autografiada",
    "higuain camiseta autografiada",
    "ortega camiseta autografiada",

    # ── Lendas mundiais vendidas no AR
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
    "mbappe camiseta autografiada",

    # ── Player issue
    "camiseta futbol player issue",
    "camiseta futbol edicion limitada numerada",
]

# ── BASQUETE (BR + AR) ─────────────────────────────────────────────────────────

BASKETBALL = [
    # ── Genérico NBA
    "camisa nba autografada",
    "jersey nba autografado",
    "camiseta nba autografiada",
    "camisa basquete autografada",
    "camiseta basquet autografiada",

    # ── Ícones absolutos
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
    "patrick ewing camisa autografada",
    "clyde drexler camisa autografada",
    "isiah thomas camisa autografada",
    "hakeem olajuwon camisa autografada",
    "dominique wilkins camisa autografada",

    # ── Modernos
    "giannis autografado camisa",
    "nikola jokic autografado camisa",
    "luka doncic autografado camisa",
    "jayson tatum autografado camisa",

    # ── Player editions
    "camisa nba match worn",
    "jersey nba player edition",
    "camisa nba game issued",
]

# ── ENJOEI (subset otimizado) ──────────────────────────────────────────────────

ENJOEI_BR = [
    "camisa futebol autografada",
    "camisa futebol autografo",
    "camisa futebol assinada jogador",
    "camisa futebol match worn",
    "camisa futebol autografada certificado",
    "pele autografado",
    "garrincha autografado",
    "zico autografado",
    "ronaldo fenomeno autografado",
    "neymar autografado camisa",
    "romario autografado",
    "ronaldinho autografado",
    "maradona autografado",
    "messi autografado camisa",
    "gabigol autografado",
    "hulk autografado camisa",
    "thiago silva autografado camisa",
    "cafu autografado",
    "roberto carlos autografado",
    "camisa futebol player issue",
    "camisa nba autografada",
    "jordan autografado",
    "kobe autografado",
    # ── Vintage / retro
    "camisa futebol vintage original",
    "camisa futebol retro original",
    "camisa copa do mundo original",
    "camisa libertadores original",
    "camisa brasil 1994 original",
    "camisa brasil 2002 original",
    "camisa joia colecionador",
    "camisa futebol original rara",
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
