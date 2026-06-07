import re
import unicodedata
from dataclasses import dataclass
from enum import Enum

from config.jerseys_catalog import CATALOG_SPORTS_CONTEXT
from config.search_terms import get_price_floor


def _normalize(text: str) -> str:
    """Remove acentos e converte para minúsculas para comparação robusta."""
    return unicodedata.normalize("NFD", text.lower()).encode("ascii", "ignore").decode("ascii")


class FlagLevel(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"


@dataclass
class RedFlag:
    code: str
    level: FlagLevel
    description: str
    penalty: int  # 0 = discard imediato, >0 = penalidade em pontos


FAKE_PATTERNS = [
    r"\bréplica\b", r"\breplica\b", r"\btailandes[a]?\b",
    r"\binspira[d][ao]\b", r"\bfake\b", r"\bimita[çc][aã]o\b",
    r"\bcópia\b", r"\bcopia\b",
    r"\bimitaci[oó]n\b", r"\breproduc[ct]i[oó]n\b",  # ES-AR
]

# Qualificadores REAIS de colecionador
COLLECTOR_QUALIFIERS = [
    # Autografado / assinado — PT e ES
    "autografad", "autógrafo", "autografo", "autograf",
    "assinad", "assinatura",
    "autografiada", "autografiado", "autógrafa",  # ES-AR
    "firmada", "firmado",  # ES: assinado
    # Inglês (eBay / Vinted EN) — com espaço para não bater "consigned", "designed"
    " signed ", "autographed",
    # Francês (Vinted FR)
    " signe ", " signee ", "dedicace", "dedicacee",
    # Match worn — usado em jogo real
    "match worn", "usada em jogo", "usada no jogo", "player worn",
    "game worn", "jogo pelo", "match issue",
    "usada en partido", "usada en juego",  # ES-AR
    # Certificações de autenticidade reconhecidas
    "coa", "certificado de autenticidade", "certificado de autenticidad",
    "psa", "beckett", "jsa", "sb brasil", "fabricks",
    # Elenco assinado (múltiplas assinaturas reais)
    "assinada elenco", "squad signed",
    # Player issue / game used — camisa de jogo original, não produto comercial
    "player issue", "player edition", "game issued", "game used",
    # Peças únicas / raridade
    "joia colecionador", "peca rara", "peca unica", "original rara",
    "edicao limitada numerada", "edicion limitada numerada",
    "numeracao limitada",
]

# Termos que indicam replica moderna vendida como "retro" — NÃO é item de colecionador
REPLICA_RETRO_TERMS = [
    "retro oficial", "retrô oficial", "retro licenciada", "retrô licenciado",
    "retro masculina", "retro feminina",  # linha de produto nova
    "licenciada oficial", "produto licenciado",
    "temporada 2024", "temporada 2025", "temporada 2026",  # camisas atuais de loja
    "nova temporada",
    # Marcas de retro licenciado — produtos em série, não vintage original
    "retrômania", "retromania", "retro mania",
    "super bolla",
    "betel ",  # Betel jerseys — retro licensed brand
    "retrô oficial",
]

# Sinais FORTES de match worn — usados para isentar SIZE_AUTOGRAPH check
# "jogo" sozinho NÃO conta — "Camisa Jogo" é só nomenclatura comercial no BR
STRONG_MATCH_WORN = [
    "match worn", "usada em jogo", "usada no jogo", "player worn",
    "game worn", "jogo pelo",
    "usada en partido", "usada en juego",
]

# Contexto de futebol (soccer) — foco principal
FOOTBALL_CONTEXT = [
    "camisa", "camiseta", "jersey", "uniforme", "maillot",
    "futebol", "football", "soccer", "futbol",
    "neymar", "zico", "pelé", "pele", "ronaldo", "romário", "romario",
    "sócrates", "socrates", "messi", "mbappé", "mbappe", "haaland",
    "maradona", "kempes", "batistuta", "riquelme", "caniggia", "tevez",
    "zanetti", "ortega", "crespo", "aimar", "saviola",
    "cr7", "r9", "r10",
    "corinthians", "flamengo", "santos", "palmeiras", "são paulo", "sao paulo",
    "vasco", "grêmio", "gremio", "internacional", "atletico", "atlético",
    "botafogo", "cruzeiro", "bahia", "sport", "fortaleza",
    "boca juniors", "river plate", "independiente", "racing", "san lorenzo",
    "huracan", "velez", "estudiantes", "lanus", "talleres",
    "brasil", "seleção", "argentina", "portugal", "espanha", "alemanha",
    "real madrid", "barcelona", "liverpool", "manchester", "chelsea", "arsenal",
    "ajax", "milan", "inter milan", "juventus", "psg", "paris saint",
    "copa do mundo", "world cup", "champions", "libertadores",
    "mundial", "copa america", "copa del mundo",  # ES-AR
]

# Contexto de basquete — foco secundário
BASKETBALL_CONTEXT = [
    "basquete", "basketball", "nba",
    "jordan", "lebron", "kobe", "magic johnson", "shaquille", "curry",
    "camisa nba", "jersey nba",
    "bulls", "lakers", "celtics", "warriors", "heat", "nets",
]

SPORTS_CONTEXT = FOOTBALL_CONTEXT + BASKETBALL_CONTEXT + CATALOG_SPORTS_CONTEXT

# Marcas esportivas — usadas para detectar camisas novas personalizadas
JERSEY_BRANDS = [
    "puma", "nike", "adidas", "umbro", "under armour",
    "penalty", "topper", "kappa", "mizuno",
]

# Tamanhos — presença no título indica camisa nova em estoque (não peça única)
JERSEY_SIZES = [" p ", " m ", " g ", " gg ", " xg ", " xgg ", " xl ", " xxl ", " 2xl ", " 3xl "]

# Linguagem de seleção de tamanho — anúncio fabricado, não item único
# Se o vendedor oferece "escolha seu tamanho", não é autógrafo real
SIZE_SELECTION_TERMS = [
    "escolha o tamanho", "escolha seu tamanho", "tamanho a escolher",
    "tamanhos disponiveis", "disponivel nos tamanhos", "todos os tamanhos",
    "tamanho p m g", "tamanho p/m/g", "p m g gg", "p/m/g/gg",
    "p/m/g/xl", "tam p m g", "tam: p", "tam: m", "tam: g",
    "pp p m g gg", "xs s m l xl", "s m l xl xxl",
    "varios tamanhos", "varios tam", "varias cores e tamanhos",
    "informar tamanho", "informe o tamanho", "informe tamanho",
    "sob medida", "escolha a cor",
]

# Anos recentes — camisa nova de temporada, não item de colecionador histórico
RECENT_YEARS = ["2024", "2025", "2026", "2027"]

# Indicadores de jogo real — exceção: match worn com marca/tamanho é legítimo
MATCH_WORN_TERMS = [
    "match worn", "usada em jogo", "player worn", "game worn", "usada no jogo",
    "jogo pelo", "usada en partido", "usada en juego",  # ES-AR
]

# ── ITEM OBRIGATORIAMENTE TÊXTIL ─────────────────────────────────────────────
# O item DEVE ser uma camisa/camiseta/jersey — bloqueia tênis, capacete,
# luvas, bola, placa, mini-capacete, macacão, poster, etc.
JERSEY_TERMS = [
    "camisa", "camiseta", "jersey", "uniforme", "maillot", "shirt",
    "kit ", " kit", "manga",  # "kit" com espaço para evitar "toolkit", etc.
]

# Termos que indicam que o item NÃO é camisa, mesmo que tenha autógrafo
NON_JERSEY_ITEMS = [
    "tênis", "tenis", "sneaker", "sapato", "calçado", "calcado",
    "chuteira", "bota esportiva",
    "capacete", "helmet", "mini capacete", "mini-capacete", "visor",
    "luva", "luvas", "glove", "gloves",
    "bola", "ball", "pelota",
    "raquete", "raqueta",
    "placa", "quadro", "poster", "pôster", "foto", "fotografia",
    "livro", "book", "revista", "magazine", "album", "álbum",
    "macacão", "macacão piloto", "overall",
    "capacete", "mini capacete", "funko", "action figure",
    "basquete autografado",  # bola de basquete — não é camisa
    "bola autografada", "bola de futebol autografada",
    "guitarra", "violão", "instrumento",
    "card ", "trading card", "cartão", "cartao",
    "acrílico", "acrilico", "display",
    # Itens de papel / impressos
    "poster", "pôster", "foto autografada", "fotografia autografada",
    "print autografado", "litografia",
]

# Termos que indicam que o item NÃO é esportivo ou é do esporte errado
NON_SPORTS_EXCLUSIONS = [
    "bateria", "tambor", "drum", "guitarra", "guitar", "baixo", "bass",
    "violão", "banda", "band", "musica", "música",
    # Música/entretenimento — CDs, DVDs, etc.
    " cd ", " cds ", "dvd", "vinil", "pagode", "samba", "funk", "sertanejo",
    "cantor", "cantora", "banda musical", "show ", "turnê",
    # Marcas de moda — não são camisas esportivas
    "lacoste", "osklen", "adidas originals",
    # Roupas que não são jersey esportivo
    "baby look", "blusa feminina", "blusa manga", "camiseta estonada",
    "polo brasil", "camisa polo",
    # Souvenirs / algodão
    "100% algodao", "100% algodão", "estonada masculina",
    # Packs de merchan — não é item único
    "kit 4 ", "kit 3 ", "kit 2 camisas",
    # Futebol americano (não é o foco)
    "nfl", "touchdown", "quarterback", "super bowl",
    # F1/motor — apenas capacete/macacão (camisa de F1 pode ser aceita em edge cases)
    "capacete", "helmet", "macacão piloto",
    # Itens comemorativos não-esportivos
    "chaveiro", "keychain", "pingente", "boneco", "miniatura",
    "telefone celular", "smartphone", "notebook", "computador",
]


def check_red_flags(listing: dict) -> list[RedFlag]:
    flags = []
    title = (listing.get("title") or "").lower()
    description = (listing.get("description") or "").lower()
    text = f"{title} {description}"
    # Versão sem acentos — para bater tanto "autógrafo" quanto "autografo", etc.
    text_n = _normalize(text)
    title_n = _normalize(title)

    # ── 1. Item deve ser têxtil (camisa/jersey) — não tênis, luva, capacete, etc.
    if not any(j in text_n for j in JERSEY_TERMS):
        flags.append(RedFlag(
            "NOT_JERSEY", FlagLevel.CRITICAL,
            "Item não é camisa/jersey — apenas camisetas e uniformes são aceitos", 0
        ))
        return flags

    if any(n in text_n for n in NON_JERSEY_ITEMS):
        flags.append(RedFlag(
            "NOT_JERSEY", FlagLevel.CRITICAL,
            "Item identificado como não-têxtil (tênis/capacete/luva/bola/etc.)", 0
        ))
        return flags

    # ── 2. Replica retro moderna (Adidas/Nike/Puma relança linha "retrô oficial")
    if any(t in text_n for t in [_normalize(t) for t in REPLICA_RETRO_TERMS]):
        flags.append(RedFlag(
            "REPLICA_RETRO", FlagLevel.CRITICAL,
            "Camisa retro licenciada/oficial atual — produto novo em série, não vintage original", 0
        ))
        return flags

    # ── 3. Camisas comemorativas / homenagem — estampam autógrafo mas não são reais
    FAKE_AUTOGRAPH_TERMS = [
        "comemorativa", "homenagem", "eterno torcedor", "coleção torcedor",
        "edição torcedor", "coloque seu nome", "personalize",
        "nome personalizado", "nome a escolher",
    ]
    if any(t in text_n for t in FAKE_AUTOGRAPH_TERMS):
        flags.append(RedFlag(
            "FAKE_AUTOGRAPH_JERSEY", FlagLevel.CRITICAL,
            "Camisa comemorativa/homenagem — autógrafo estampado, não real", 0
        ))
        return flags

    # ── 3. Seleção de tamanho = produção em série com autógrafo silkado
    if any(t in text_n for t in SIZE_SELECTION_TERMS):
        flags.append(RedFlag(
            "SIZE_SELECTION_JERSEY", FlagLevel.CRITICAL,
            "Anúncio oferece escolha de tamanho — camisa fabricada em série, autógrafo não é real", 0
        ))
        return flags

    # ── 4. Qualificador de colecionador obrigatório
    if not any(q in text_n for q in [_normalize(q) for q in COLLECTOR_QUALIFIERS]):
        flags.append(RedFlag(
            "NOT_COLLECTOR_GRADE", FlagLevel.CRITICAL,
            "Item sem qualificador de colecionador (autografado/match worn/COA)", 0
        ))
        return flags

    # ── 5. Versão jogador sem autógrafo/COA = camisa comercial cara, não colecionador
    PLAYER_VERSION_TERMS = ["versao jogador", "version jogador", "versão jogador", "version jugador"]
    has_autograph_or_coa = any(t in text_n for t in [
        "autograf", "assinad", "firmad", "autographed",
        "coa", "psa", "beckett", "jsa",
    ]) or " signed " in padded or " signe " in padded
    if any(t in text_n for t in PLAYER_VERSION_TERMS) and not has_autograph_or_coa:
        flags.append(RedFlag(
            "PLAYER_VERSION_NO_AUTH", FlagLevel.CRITICAL,
            "Versão jogador sem autógrafo ou COA — camisa comercial, não item de colecionador", 0
        ))
        return flags

    # Detecta camisa fabricada: marca + tamanho + ano recente OU tamanho + autógrafo (produção em série)
    padded = f" {text_n} "
    has_brand = any(b in padded for b in JERSEY_BRANDS)
    has_size = any(s in padded for s in JERSEY_SIZES)
    has_recent_year = any(y in text_n for y in RECENT_YEARS)
    is_strong_match_worn = any(m in text_n for m in [_normalize(m) for m in STRONG_MATCH_WORN])
    is_match_worn = is_strong_match_worn or any(m in text_n for m in [_normalize(m) for m in MATCH_WORN_TERMS])
    has_autograph_claim = any(t in text_n for t in [
        "autograf", "assinad", "firmad", "autographed",
    ]) or " signed " in padded or " signe " in padded

    # Caso clássico: marca + tamanho + ano recente = estoque de loja
    if has_brand and has_size and has_recent_year and not is_match_worn:
        flags.append(RedFlag(
            "PERSONALIZED_JERSEY", FlagLevel.CRITICAL,
            "Camisa nova personalizada (marca + tamanho + ano recente) — não é autógrafo real", 0
        ))
        return flags

    # Múltiplos tamanhos + autógrafo = produção em série com autógrafo silkado.
    # Um único tamanho descrito é legítimo — a regra original bloqueava demais.
    size_count = sum(1 for s in JERSEY_SIZES if s in padded)
    if size_count >= 2 and has_autograph_claim and not is_strong_match_worn:
        flags.append(RedFlag(
            "SIZE_AUTOGRAPH_JERSEY", FlagLevel.CRITICAL,
            "Múltiplos tamanhos + autógrafo = camisa fabricada em série com autógrafo silkado", 0
        ))
        return flags

    # Rejeita itens não-esportivos que passaram pelo qualificador
    if any(ex in text_n for ex in NON_SPORTS_EXCLUSIONS):
        flags.append(RedFlag(
            "NOT_SPORTS_ITEM", FlagLevel.CRITICAL,
            "Item de categoria não-esportiva (música, livro, etc.)", 0
        ))
        return flags

    if not any(ctx in text_n for ctx in [_normalize(ctx) for ctx in SPORTS_CONTEXT]):
        flags.append(RedFlag(
            "NO_SPORTS_CONTEXT", FlagLevel.CRITICAL,
            "Sem contexto esportivo identificável no título/descrição", 0
        ))
        return flags

    for pattern in FAKE_PATTERNS:
        if re.search(pattern, text_n, re.IGNORECASE):
            flags.append(RedFlag(
                "EXPLICIT_FAKE", FlagLevel.CRITICAL,
                f"Termo de produto falso detectado no texto", 0
            ))
            break

    # ── Preço abaixo do piso para o tipo de item ─────────────────────────────
    # Usa versão normalizada do título para pegar "autógrafo" com acento
    listing_n = {**listing, "title": _normalize(listing.get("title") or "")}
    price = listing.get("price", 0)
    floor = get_price_floor(listing_n)
    if price > 0 and price < floor:
        flags.append(RedFlag(
            "BELOW_PRICE_FLOOR", FlagLevel.CRITICAL,
            f"Preço R${price:.0f} abaixo do mínimo R${floor:.0f} para este tipo de item "
            f"— autógrafo real de lenda/COA não existe neste valor", 0
        ))
        return flags

    images = listing.get("images") or []
    if not images:
        flags.append(RedFlag("NO_IMAGES", FlagLevel.HIGH, "Anúncio sem imagens", 100))
    elif len(images) == 1:
        flags.append(RedFlag("SINGLE_IMAGE", FlagLevel.MEDIUM, "Apenas 1 foto", 5))

    seller = listing.get("seller") or {}
    price = listing.get("price", 0)
    if seller.get("total_ratings", 0) == 0 and price > 500:
        flags.append(RedFlag(
            "NEW_SELLER_HIGH_VALUE", FlagLevel.HIGH,
            f"Vendedor sem avaliações com item de R${price:.0f}", 100
        ))

    return flags


def has_critical_flag(flags: list[RedFlag]) -> bool:
    return any(f.level == FlagLevel.CRITICAL or f.penalty == 0 for f in flags)


def calculate_flag_penalty(flags: list[RedFlag]) -> int:
    return sum(f.penalty for f in flags if 0 < f.penalty < 100)
