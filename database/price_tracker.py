"""
Preços de referência de VENDA calibrados com dados do mercado BR (mai/2026).
Fontes: Prime Collection Brasil, mercado secundário ML/Enjoei, leilões Goldin.

Estratégia: comprar em plataformas secundárias (ML, Enjoei, AR) a 40-60% do
preço de venda e revender em canais collector (Instagram, Catawiki, leilões).
"""

import logging

from sqlalchemy import func, select

from .db import AsyncSessionLocal
from .models import Tier3Price
from config.jerseys_catalog import get_catalog_price_reference

logger = logging.getLogger(__name__)

# ── Preços de VENDA estimados (o que você vai receber ao revender) ─────────────
# Calibrados com: Prime Collection Brasil + pesquisa de mercado mai/2026
FALLBACK_PRICES = {

    # ── ÍCONES — FUTEBOL ──────────────────────────────────────────────────────
    "pele_autografada":          12000,
    "pele_match_worn":           30000,
    "pele_retro":                 2500,

    "maradona_autografada":      15000,
    "maradona_match_worn":       40000,
    "maradona_retro":             3000,

    "messi_autografada":          8000,
    "messi_match_worn":          30000,
    "messi_retro":                2000,

    "ronaldo_cr7_autografada":    6000,
    "ronaldo_cr7_match_worn":    20000,
    "ronaldo_cr7_retro":          1500,

    # ── LENDAS BRASILEIRAS ────────────────────────────────────────────────────
    "zico_autografada":           2000,
    "zico_match_worn":            6000,
    "zico_retro":                  500,

    "ronaldo_fenomeno_autografada": 4990,
    "ronaldo_fenomeno_match_worn": 12000,
    "ronaldo_fenomeno_retro":       900,

    "romario_autografada":        2500,
    "romario_match_worn":         7000,
    "romario_retro":               600,

    "socrates_autografada":       3500,
    "socrates_match_worn":        9000,
    "socrates_retro":              800,

    "ronaldinho_autografada":     3000,
    "ronaldinho_match_worn":      9000,
    "ronaldinho_retro":            700,

    "rivaldo_autografada":        2790,
    "rivaldo_match_worn":         8000,
    "rivaldo_retro":               650,

    "kaka_autografada":           2800,
    "kaka_match_worn":            8000,
    "kaka_retro":                  650,

    "adriano_autografada":        1800,
    "adriano_match_worn":         5000,
    "adriano_retro":               450,

    "bebeto_autografada":         1800,
    "bebeto_match_worn":          5000,
    "bebeto_retro":                400,

    "cafu_autografada":           1500,
    "cafu_match_worn":            4500,
    "cafu_retro":                  400,

    "roberto_carlos_autografada": 2000,
    "roberto_carlos_match_worn":  6000,
    "roberto_carlos_retro":        500,

    "neymar_autografada":         1800,
    "neymar_match_worn":          5500,
    "neymar_retro":                450,

    "vinicius_jr_autografada":    2200,
    "vinicius_jr_match_worn":     6000,
    "vinicius_jr_retro":           500,

    "gabriel_martinelli_autografada": 2690,
    "gabriel_martinelli_match_worn":  6000,
    "gabriel_martinelli_retro":       500,

    "dani_alves_autografada":     1200,
    "dani_alves_retro":            350,

    "thiago_silva_autografada":   1200,
    "thiago_silva_retro":          350,

    "dunga_autografada":          1500,
    "dunga_retro":                 400,

    # ── LENDAS ARGENTINAS ─────────────────────────────────────────────────────
    "batistuta_autografada":      2690,
    "batistuta_match_worn":       7500,
    "batistuta_retro":             600,

    "riquelme_autografada":       2500,
    "riquelme_match_worn":        7000,
    "riquelme_retro":              550,

    "kempes_autografada":         2200,
    "kempes_match_worn":          8000,
    "kempes_retro":                700,

    "caniggia_autografada":       1800,
    "caniggia_match_worn":        5000,
    "caniggia_retro":              450,

    "zanetti_autografada":        2000,
    "zanetti_match_worn":         5500,
    "zanetti_retro":               500,

    "tevez_autografada":          1600,
    "tevez_match_worn":           4500,
    "tevez_retro":                 420,

    "aguero_autografada":         2690,
    "aguero_match_worn":          7000,
    "aguero_retro":                600,

    "di_maria_autografada":       1800,
    "di_maria_match_worn":        5000,
    "di_maria_retro":              450,

    "crespo_autografada":         2690,
    "crespo_match_worn":          6000,
    "crespo_retro":                550,

    "mascherano_autografada":     2200,
    "mascherano_match_worn":      6000,
    "mascherano_retro":            500,

    "veron_autografada":          1500,
    "veron_match_worn":           4000,
    "veron_retro":                 400,

    "higuain_autografada":        1500,
    "higuain_match_worn":         4000,
    "higuain_retro":               380,

    "lautaro_autografada":        2000,
    "lautaro_match_worn":         5500,
    "lautaro_retro":               480,

    # ── EUROPA — ITÁLIA ───────────────────────────────────────────────────────
    "totti_autografada":          2790,
    "totti_match_worn":           8000,
    "totti_retro":                 650,

    "maldini_autografada":        3200,
    "maldini_match_worn":         9000,
    "maldini_retro":               700,

    "del_piero_autografada":      2800,
    "del_piero_match_worn":       8000,
    "del_piero_retro":             650,

    "buffon_autografada":         2500,
    "buffon_match_worn":          7000,
    "buffon_retro":                580,

    "baggio_autografada":         3000,
    "baggio_match_worn":          9000,
    "baggio_retro":                700,

    "inzaghi_autografada":        2000,
    "inzaghi_match_worn":         5500,
    "inzaghi_retro":               500,

    "cannavaro_autografada":      2990,
    "cannavaro_match_worn":       7000,
    "cannavaro_retro":             600,

    "shevchenko_autografada":     2500,
    "shevchenko_match_worn":      7000,
    "shevchenko_retro":            580,

    "seedorf_autografada":        2690,
    "seedorf_match_worn":         6500,
    "seedorf_retro":               550,

    # ── EUROPA — HOLANDA ──────────────────────────────────────────────────────
    "van_basten_autografada":     3000,
    "van_basten_match_worn":      9000,
    "van_basten_retro":            700,

    "gullit_autografada":         2800,
    "gullit_match_worn":          8000,
    "gullit_retro":                650,

    "kluivert_autografada":       2690,
    "kluivert_match_worn":        6500,
    "kluivert_retro":              550,

    # ── EUROPA — ESPANHA ──────────────────────────────────────────────────────
    "raul_autografada":           2500,
    "raul_match_worn":            7000,
    "raul_retro":                  580,

    "iniesta_autografada":        2800,
    "iniesta_match_worn":         7500,
    "iniesta_retro":               620,

    "xavi_autografada":           2500,
    "xavi_match_worn":            7000,
    "xavi_retro":                  580,

    "torres_autografada":         2690,
    "torres_match_worn":          6500,
    "torres_retro":                550,

    # ── EUROPA — PORTUGAL ─────────────────────────────────────────────────────
    "figo_autografada":           2800,
    "figo_match_worn":            7500,
    "figo_retro":                  620,

    # ── EUROPA — ENGLAND ──────────────────────────────────────────────────────
    "beckham_autografada":        2800,
    "beckham_match_worn":         8000,
    "beckham_retro":               650,

    "gerrard_autografada":        2200,
    "gerrard_match_worn":         6500,
    "gerrard_retro":               550,

    "rooney_autografada":         2000,
    "rooney_match_worn":          5500,
    "rooney_retro":                480,

    "bale_autografada":           3790,
    "bale_match_worn":            8500,
    "bale_retro":                  700,

    # ── OUTROS ────────────────────────────────────────────────────────────────
    "suarez_autografada":         2690,
    "suarez_match_worn":          7000,
    "suarez_retro":                580,

    "drogba_autografada":         2500,
    "drogba_match_worn":          7000,
    "drogba_retro":                580,

    "higuita_autografada":        3690,
    "higuita_match_worn":         8000,
    "higuita_retro":               700,

    "ballack_autografada":        3990,
    "ballack_match_worn":         9000,
    "ballack_retro":               750,

    "zidane_autografada":        12000,   # Prime Collection: R$12.000
    "zidane_match_worn":         25000,
    "zidane_retro":               1500,

    "henry_autografada":          2500,
    "henry_match_worn":           7000,
    "henry_retro":                 580,

    # ── F1 — REFERÊNCIA (se aparecer camisa/uniforme) ─────────────────────────
    "senna_autografada":         30000,
    "senna_retro":                5000,

    # ── NBA ───────────────────────────────────────────────────────────────────
    "michael_jordan_autografado": 15000,
    "michael_jordan_match_worn":  50000,
    "michael_jordan_retro":        3000,

    "kobe_bryant_autografado":    12000,
    "kobe_bryant_match_worn":     40000,
    "kobe_bryant_retro":           2500,

    "lebron_james_autografado":    8000,
    "lebron_james_match_worn":    30000,
    "lebron_james_retro":          2000,

    "magic_johnson_autografado":   7990,   # Prime: R$7.990 (USA camisa)
    "magic_johnson_match_worn":   20000,
    "magic_johnson_retro":         1500,

    "larry_bird_autografado":      6990,   # Prime: R$6.990
    "larry_bird_match_worn":      18000,
    "larry_bird_retro":            1400,

    "shaquille_oneal_autografado": 4000,
    "shaquille_oneal_match_worn": 14000,
    "shaquille_oneal_retro":       1000,

    "stephen_curry_autografado":   6500,   # Prime: R$6.500
    "stephen_curry_match_worn":   18000,
    "stephen_curry_retro":         1500,

    "allen_iverson_autografado":   3690,   # Prime: R$3.690
    "allen_iverson_match_worn":   10000,
    "allen_iverson_retro":          900,

    "scottie_pippen_autografado":  3000,
    "scottie_pippen_match_worn":   9000,
    "scottie_pippen_retro":         750,

    "dennis_rodman_autografado":   3000,   # Prime: R$3.000 (camisa)
    "dennis_rodman_match_worn":    9000,
    "dennis_rodman_retro":          750,

    "charles_barkley_autografado": 3500,
    "charles_barkley_match_worn": 10000,
    "charles_barkley_retro":        850,

    "kevin_durant_autografado":    4490,   # Prime: R$4.490
    "kevin_durant_match_worn":    14000,
    "kevin_durant_retro":          1100,

    "karl_malone_autografado":     3000,
    "karl_malone_retro":            750,

    "john_stockton_autografado":   2800,
    "john_stockton_retro":          700,

    "dwyane_wade_autografado":     3500,
    "dwyane_wade_retro":            900,

    "dirk_nowitzki_autografado":   4000,
    "dirk_nowitzki_retro":         1000,

    "tim_duncan_autografado":      3500,
    "tim_duncan_retro":             900,

    # ── VINTAGE / RETRO POR CLUBE (calibrado pelo catálogo pessoal) ───────────────
    # Fonte: planilha de estoque "CATÁLOGO DE CAMISAS ORIGINAIS" (49 peças, mai/2026)
    # Valores = faixa média de revenda BR para camisas originais em excelente conservação

    "brasil_copa_2002":            1100,   # Catálogo lote 49 — pentacampeão, JOIA
    "brasil_copa_1998":             950,   # Catálogo lote 8 — R9 crise, JOIA
    "brasil_copa_2019":             425,   # Catálogo lote 7 — Copa América
    "italia_copa_2006":             825,   # Catálogo lote 30 — campeã, JOIA
    "alemanha_copa_2014":           825,   # Catálogo lote 20 — campeã 7x1, JOIA
    "argentina_copa_2014":          800,   # Catálogo lote 19 — vice-campeã, JOIA
    "franca_copa_2018":             650,   # Catálogo lote 25 — campeã, JOIA
    "espanha_copa_2010":            775,   # Catálogo lote 40 — campeã, JOIA
    "portugal_euro_2016":           540,   # Catálogo lote 24 — campeã, RARO
    "barcelona_2014_15":            740,   # Catálogo lote 28 — triplete MSN, JOIA
    "barcelona_2011_12":            550,   # Catálogo lote 13 — era Guardiola, RARO
    "atletico_2013_14":             700,   # Catálogo lote 18 — campeão La Liga, JOIA
    "flamengo_2019":                650,   # Catálogo lote 33 — Libertadores, JOIA
    "santos_2011":                  775,   # Catálogo lote 34 — Neymar Libertadores, JOIA
    "corinthians_2012":             510,   # Catálogo lote 35 — campeão mundial, RARO
    "inter_milan_1996_97":          750,   # Catálogo lote 11 — era R9 Umbro, RARO
    "inter_milan_2014_15":          340,   # Catálogo lote 3
    "roma_2000_01":                 680,   # Catálogo lote 12 — scudetto Kappa, RARO
    "roma_2019_20":                 375,   # Catálogo lote 2
    "ajax_1994_95":                 975,   # Catálogo lote 22 — Champions Umbro, JOIA
    "marseille_1992_93":            900,   # Catálogo lote 37 — único Champions, JOIA
    "milan_2006_07":                620,   # Catálogo lote 15 — Champions, RARO
    "napoli_2022_23":               575,   # Catálogo lote 39 — scudetto 33 anos, RARO
    "liverpool_2017_18":            580,   # Catálogo lote 14 — manga longa, RARO
    "chelsea_2011_12":              510,   # Catálogo lote 21 — Champions, RARO
    "rangers_2012_13":              350,   # Catálogo lote 1 — rebaixamento histórico, RARO
    "psg_jordan_2018_19":           650,   # Catálogo lote 10 — 1ª collab Jordan, RARO
    "boca_2015":                    450,   # Catálogo lote 6 — centenário
    "river_2018":                   480,   # Catálogo lote 43 — Libertadores, RARO
    "gremio_2017":                  445,   # Catálogo lote 44 — Libertadores, RARO
    "everton_2018_19_assinada":     900,   # Catálogo lote 9 — elenco completo, JOIA

    # ── SQUAD SIGNED — seleções e clubes ─────────────────────────────────────
    # Camisas assinadas pelo elenco completo valem mais que autógrafo único genérico
    "selecao_brasil_copa98_squad":  4500,  # Brasil 98 (R9, Ronaldinho, Bebeto, Rivaldo…)
    "selecao_brasil_copa2002_squad":5000,  # Brasil 2002 pentacampeão (R9, Ronaldinho, Rivaldo…)
    "selecao_brasil_squad":         2800,  # seleção genérica squad signed
    "selecao_argentina_squad":      2500,
    "santos_squad":                 1800,  # Santos squad (clube histórico)
    "flamengo_squad":               1800,
    "generic_squad_signed":         2000,  # elenco de clube sem identificação
    "generic_squad_autografada":    2000,

    # ── GENÉRICOS (fallback por tipo) ─────────────────────────────────────────
    "generic_autografada":         1200,
    "generic_autografado":         1200,
    "generic_match_worn":          2500,
    "generic_retro":                600,
    "generic_championship":         800,
    "generic_player_issue":        1000,
    "generic_nba":                 1800,
    "generic_vintage_joia":         850,   # camisa vintage joia sem player known
    "generic_vintage_raro":         500,   # camisa vintage rara sem player known
    "generic_vintage_copa":         700,   # camisa de Copa do Mundo sem player known
}

# ── Aliases de nome → slug do dicionário ──────────────────────────────────────
_NAME_ALIASES = {
    "pelé": "pele", "pele": "pele",
    "maradona": "maradona", "diego maradona": "maradona",
    "messi": "messi", "leo messi": "messi", "lionel messi": "messi",
    "cr7": "ronaldo_cr7", "cristiano ronaldo": "ronaldo_cr7",
    "zico": "zico",
    "ronaldo fenomeno": "ronaldo_fenomeno", "ronaldo nazário": "ronaldo_fenomeno",
    "r9": "ronaldo_fenomeno", "ronaldo r9": "ronaldo_fenomeno",
    "romario": "romario", "romário": "romario",
    "socrates": "socrates", "sócrates": "socrates",
    "ronaldinho": "ronaldinho", "r10": "ronaldinho",
    "ronaldinho gaúcho": "ronaldinho", "ronaldinho gaucho": "ronaldinho",
    "rivaldo": "rivaldo",
    "kaká": "kaka", "kaka": "kaka", "ricardo kaká": "kaka",
    "adriano": "adriano", "adriano imperador": "adriano",
    "bebeto": "bebeto",
    "cafu": "cafu",
    "roberto carlos": "roberto_carlos",
    "neymar": "neymar", "neymar jr": "neymar",
    "vinicius jr": "vinicius_jr", "vini jr": "vinicius_jr",
    "martinelli": "gabriel_martinelli", "gabriel martinelli": "gabriel_martinelli",
    "dani alves": "dani_alves", "daniel alves": "dani_alves",
    "thiago silva": "thiago_silva",
    "dunga": "dunga",
    "batistuta": "batistuta", "gabriel batistuta": "batistuta", "batigol": "batistuta",
    "riquelme": "riquelme", "juan román riquelme": "riquelme",
    "kempes": "kempes", "mario kempes": "kempes",
    "caniggia": "caniggia",
    "zanetti": "zanetti", "javier zanetti": "zanetti",
    "tevez": "tevez", "carlos tevez": "tevez",
    "agüero": "aguero", "aguero": "aguero", "kun agüero": "aguero", "sergio agüero": "aguero",
    "di maría": "di_maria", "di maria": "di_maria", "ángel di maría": "di_maria",
    "crespo": "crespo", "hernán crespo": "crespo",
    "mascherano": "mascherano", "javier mascherano": "mascherano",
    "verón": "veron", "veron": "veron",
    "higuaín": "higuain", "higuain": "higuain",
    "lautaro": "lautaro", "lautaro martínez": "lautaro",
    "totti": "totti", "francesco totti": "totti",
    "maldini": "maldini", "paolo maldini": "maldini",
    "del piero": "del_piero", "alessandro del piero": "del_piero",
    "buffon": "buffon", "gianluigi buffon": "buffon",
    "baggio": "baggio", "roberto baggio": "baggio",
    "inzaghi": "inzaghi", "filippo inzaghi": "inzaghi",
    "cannavaro": "cannavaro", "fabio cannavaro": "cannavaro",
    "shevchenko": "shevchenko", "andriy shevchenko": "shevchenko",
    "seedorf": "seedorf", "clarence seedorf": "seedorf",
    "van basten": "van_basten", "marco van basten": "van_basten",
    "gullit": "gullit", "ruud gullit": "gullit",
    "kluivert": "kluivert", "patrick kluivert": "kluivert",
    "raúl": "raul", "raul": "raul",
    "iniesta": "iniesta", "andrés iniesta": "iniesta",
    "xavi": "xavi", "xavi hernández": "xavi",
    "torres": "torres", "fernando torres": "torres",
    "figo": "figo", "luís figo": "figo",
    "beckham": "beckham", "david beckham": "beckham",
    "gerrard": "gerrard", "steven gerrard": "gerrard",
    "rooney": "rooney", "wayne rooney": "rooney",
    "bale": "bale", "gareth bale": "bale",
    "suárez": "suarez", "suarez": "suarez", "luis suárez": "suarez",
    "drogba": "drogba", "didier drogba": "drogba",
    "higuita": "higuita", "rené higuita": "higuita",
    "ballack": "ballack", "michael ballack": "ballack",
    "zidane": "zidane", "zinedine zidane": "zidane",
    "henry": "henry", "thierry henry": "henry",
    "senna": "senna", "ayrton senna": "senna",
    "michael jordan": "michael_jordan", "jordan": "michael_jordan",
    "kobe": "kobe_bryant", "kobe bryant": "kobe_bryant",
    "lebron": "lebron_james", "lebron james": "lebron_james",
    "magic johnson": "magic_johnson", "magic": "magic_johnson",
    "larry bird": "larry_bird", "bird": "larry_bird",
    "shaq": "shaquille_oneal", "shaquille": "shaquille_oneal", "shaquille oneal": "shaquille_oneal",
    "curry": "stephen_curry", "stephen curry": "stephen_curry", "steph curry": "stephen_curry",
    "allen iverson": "allen_iverson", "iverson": "allen_iverson",
    "pippen": "scottie_pippen", "scottie pippen": "scottie_pippen",
    "rodman": "dennis_rodman", "dennis rodman": "dennis_rodman",
    "barkley": "charles_barkley", "charles barkley": "charles_barkley",
    "kevin durant": "kevin_durant", "durant": "kevin_durant",
    "karl malone": "karl_malone", "malone": "karl_malone",
    "john stockton": "john_stockton", "stockton": "john_stockton",
    "dwyane wade": "dwyane_wade", "wade": "dwyane_wade",
    "dirk nowitzki": "dirk_nowitzki", "dirk": "dirk_nowitzki",
    "tim duncan": "tim_duncan", "duncan": "tim_duncan",
}


def _normalize_player(player_name: str) -> str:
    return _NAME_ALIASES.get(player_name.lower().strip(), "")


_SQUAD_SIGNALS = [
    "elenco", "jogadores", "squad signed", "assinada elenco", "assinado jogadores",
    "varios jogadores", "varios autografos", "squad autografada",
    "autografada jogadores", "autografado jogadores",
]

def _squad_key_from_title(title: str) -> str:
    """Retorna chave de preço para squad signed baseada no título."""
    t = title.lower()
    if "brasil" in t or "seleção" in t or "selecao" in t or "cbf" in t:
        if "98" in t or "1998" in t:
            return "selecao_brasil_copa98_squad"
        if "2002" in t or "02" in t:
            return "selecao_brasil_copa2002_squad"
        return "selecao_brasil_squad"
    if "argentina" in t:
        return "selecao_argentina_squad"
    if "santos" in t:
        return "santos_squad"
    if "flamengo" in t:
        return "flamengo_squad"
    return "generic_squad_signed"


async def get_sell_price_estimate(player_name: str, item_type: str = "autografada", title: str = "") -> float:
    # 0. Squad signed — elenco assinado tem preço específico por time/era
    if title and any(s in title.lower() for s in _SQUAD_SIGNALS):
        key = _squad_key_from_title(title)
        price = FALLBACK_PRICES.get(key, FALLBACK_PRICES["generic_squad_signed"])
        logger.debug(f"[Price] Squad signed '{key}': R${price}")
        return float(price)

    # 1. Tenta do banco de dados (preços reais coletados pelo tier3)
    if player_name:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(func.avg(Tier3Price.price)).where(
                    Tier3Price.player_name.ilike(f"%{player_name}%"),
                    Tier3Price.item_type == item_type,
                )
            )
            avg = result.scalar()
            if avg and avg > 0:
                logger.debug(f"[Price] Tier3 avg '{player_name}': R${avg:.0f}")
                return float(avg)

    # 2. Lookup pelo alias → slug
    slug = _normalize_player(player_name)
    if slug:
        key = f"{slug}_{item_type}"
        price = FALLBACK_PRICES.get(key)
        if price:
            logger.debug(f"[Price] Fallback '{player_name}' {item_type}: R${price}")
            return float(price)

    # 3. Gera slug genérico e tenta
    if player_name:
        raw_slug = player_name.lower().strip()
        for old, new in [("é","e"),("ê","e"),("ã","a"),("ô","o"),("ó","o"),
                         ("á","a"),("à","a"),("ú","u"),("ç","c"),(" ","_")]:
            raw_slug = raw_slug.replace(old, new)
        key = f"{raw_slug}_{item_type}"
        price = FALLBACK_PRICES.get(key)
        if price:
            return float(price)

    # 4. Catálogo pessoal — vintage/retro jerseys do estoque do operador
    # Usado para estimar preço de camisas sem jogador específico (Copa 2002, Flamengo 2019, etc.)
    # get_catalog_price_reference espera o título completo do anúncio
    # Aqui fazemos lookup pelo player_name como fallback de título
    if player_name:
        catalog_ref = get_catalog_price_reference(player_name)
        if catalog_ref:
            vl_min, vl_max = catalog_ref
            vl_medio = (vl_min + vl_max) / 2
            logger.debug(f"[Price] Catálogo pessoal '{player_name}': R${vl_medio:.0f}")
            return vl_medio

    # 5. Fallback genérico por tipo
    generic_key = f"generic_{item_type}"
    price = FALLBACK_PRICES.get(generic_key, 1000)
    logger.debug(f"[Price] Fallback genérico '{player_name}' {item_type}: R${price}")
    return float(price)
