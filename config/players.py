"""
Banco completo de atletas colecionáveis.
Referência de preços calibrada com dados do mercado brasileiro (mai/2026).

Hierarquia de raridade:
  icon     — demanda global, giro ≤21d (Pelé, Maradona, Jordan, Senna)
  legend   — demanda forte, giro 30–60d
  rare     — demanda nicho, giro 60–150d
  regional — demanda local, giro 150–365d
"""

from datetime import date

# ─────────────────────────────────────────────────────────────────────────────
# FUTEBOL — BRASIL
# ─────────────────────────────────────────────────────────────────────────────

PLAYERS = {

    "pele": {
        "nomes_busca": ["Pelé", "Pele", "Edson Arantes", "Edson Arantes do Nascimento", "O Rei"],
        "clubes": ["Santos", "New York Cosmos", "Brasil"],
        "pais": "BR", "esporte": "football",
        "raridade": "icon", "liquidez_dias": 14,
        "preco_referencia": {"autografada": 12000, "match_worn": 30000, "retro": 2500},
        "copa_2026": False, "controversias_ativas": [],
        "eventos_futuros": [],
        "tags": ["santos", "brasil", "copa58", "copa62", "copa70", "icon", "pele", "cosmos"],
    },

    "zico": {
        "nomes_busca": ["Zico", "Arthur Antunes Coimbra", "Galinho de Quintino", "Galinho"],
        "clubes": ["Flamengo", "Udinese", "Kashima Antlers", "Brasil"],
        "pais": "BR", "esporte": "football",
        "raridade": "legend", "liquidez_dias": 45,
        "preco_referencia": {"autografada": 2000, "match_worn": 6000, "retro": 500},
        "copa_2026": False, "controversias_ativas": [],
        "eventos_futuros": [],
        "tags": ["flamengo", "brasil", "copa82", "galinho"],
    },

    "ronaldo_fenomeno": {
        "nomes_busca": ["Ronaldo Fenômeno", "Ronaldo Nazário", "R9", "Ronaldo R9", "Ronaldo Lima", "Ronaldo Gordo"],
        "clubes": ["Cruzeiro", "PSV", "Barcelona", "Inter", "Real Madrid", "Brasil"],
        "pais": "BR", "esporte": "football",
        "raridade": "legend", "liquidez_dias": 35,
        "preco_referencia": {"autografada": 4990, "match_worn": 12000, "retro": 900},
        "copa_2026": False, "controversias_ativas": [],
        "eventos_futuros": [],
        "tags": ["r9", "inter", "real_madrid", "brasil", "copa94", "copa98", "copa02"],
    },

    "romario": {
        "nomes_busca": ["Romário", "Romario", "Baixinho", "Romário de Souza Faria"],
        "clubes": ["Vasco", "PSV", "Barcelona", "Flamengo", "Brasil"],
        "pais": "BR", "esporte": "football",
        "raridade": "legend", "liquidez_dias": 50,
        "preco_referencia": {"autografada": 2500, "match_worn": 7000, "retro": 600},
        "copa_2026": False, "controversias_ativas": [],
        "eventos_futuros": [],
        "tags": ["vasco", "barcelona", "brasil", "copa94", "baixinho"],
    },

    "socrates": {
        "nomes_busca": ["Sócrates", "Socrates", "Dr. Sócrates", "Sócrates Brasileiro"],
        "clubes": ["Corinthians", "Fiorentina", "Brasil"],
        "pais": "BR", "esporte": "football",
        "raridade": "legend", "liquidez_dias": 55,
        "preco_referencia": {"autografada": 3500, "match_worn": 9000, "retro": 800},
        "copa_2026": False, "controversias_ativas": [],
        "eventos_futuros": [],
        "tags": ["corinthians", "brasil", "copa82", "doutor"],
    },

    "ronaldinho": {
        "nomes_busca": ["Ronaldinho", "Ronaldinho Gaúcho", "R10", "Ronaldinho Gaucho", "Ronaldinho Barcelone"],
        "clubes": ["Grêmio", "PSG", "Barcelona", "Milan", "Flamengo", "Brasil"],
        "pais": "BR", "esporte": "football",
        "raridade": "legend", "liquidez_dias": 30,
        "preco_referencia": {"autografada": 3000, "match_worn": 9000, "retro": 700},
        "copa_2026": False, "controversias_ativas": [],
        "eventos_futuros": [],
        "tags": ["r10", "barcelona", "milan", "brasil", "copa02", "bola_de_ouro"],
    },

    "rivaldo": {
        "nomes_busca": ["Rivaldo", "Rivaldo Vítor Borba Ferreira"],
        "clubes": ["Barcelona", "Milan", "Brasil"],
        "pais": "BR", "esporte": "football",
        "raridade": "legend", "liquidez_dias": 55,
        "preco_referencia": {"autografada": 2790, "match_worn": 8000, "retro": 650},
        "copa_2026": False, "controversias_ativas": [],
        "eventos_futuros": [],
        "tags": ["barcelona", "brasil", "copa98", "copa02", "bola_de_ouro"],
    },

    "kaka": {
        "nomes_busca": ["Kaká", "Kaka", "Ricardo Kaká", "Ricardo Izecson"],
        "clubes": ["São Paulo", "Milan", "Real Madrid", "Brasil"],
        "pais": "BR", "esporte": "football",
        "raridade": "legend", "liquidez_dias": 45,
        "preco_referencia": {"autografada": 2800, "match_worn": 8000, "retro": 650},
        "copa_2026": False, "controversias_ativas": [],
        "eventos_futuros": [],
        "tags": ["milan", "real_madrid", "brasil", "bola_de_ouro"],
    },

    "adriano": {
        "nomes_busca": ["Adriano", "Adriano Leite Ribeiro", "Adriano Imperador"],
        "clubes": ["Flamengo", "Inter", "Roma", "Brasil"],
        "pais": "BR", "esporte": "football",
        "raridade": "rare", "liquidez_dias": 80,
        "preco_referencia": {"autografada": 1800, "match_worn": 5000, "retro": 450},
        "copa_2026": False, "controversias_ativas": [],
        "eventos_futuros": [],
        "tags": ["inter", "flamengo", "brasil", "imperador"],
    },

    "bebeto": {
        "nomes_busca": ["Bebeto", "José Roberto Gama de Oliveira"],
        "clubes": ["Vasco", "Flamengo", "Deportivo", "Brasil"],
        "pais": "BR", "esporte": "football",
        "raridade": "legend", "liquidez_dias": 70,
        "preco_referencia": {"autografada": 1800, "match_worn": 5000, "retro": 400},
        "copa_2026": False, "controversias_ativas": [],
        "eventos_futuros": [],
        "tags": ["flamengo", "brasil", "copa94"],
    },

    "cafu": {
        "nomes_busca": ["Cafu", "Marcos Evangelista de Morais", "Il Pendolino"],
        "clubes": ["São Paulo", "Roma", "Milan", "Brasil"],
        "pais": "BR", "esporte": "football",
        "raridade": "legend", "liquidez_dias": 70,
        "preco_referencia": {"autografada": 1500, "match_worn": 4500, "retro": 400},
        "copa_2026": False, "controversias_ativas": [],
        "eventos_futuros": [],
        "tags": ["sao_paulo", "roma", "brasil", "copa94", "copa02"],
    },

    "roberto_carlos": {
        "nomes_busca": ["Roberto Carlos", "Roberto Carlos da Silva", "RC3"],
        "clubes": ["Real Madrid", "Brasil", "Fenerbahçe"],
        "pais": "BR", "esporte": "football",
        "raridade": "legend", "liquidez_dias": 60,
        "preco_referencia": {"autografada": 2000, "match_worn": 6000, "retro": 500},
        "copa_2026": False, "controversias_ativas": [],
        "eventos_futuros": [],
        "tags": ["real_madrid", "brasil", "copa02"],
    },

    "neymar": {
        "nomes_busca": ["Neymar", "Neymar Jr", "NJR", "Neymar da Silva Santos"],
        "clubes": ["Santos", "Barcelona", "PSG", "Al-Hilal", "Santos", "Brasil"],
        "pais": "BR", "esporte": "football",
        "raridade": "rare", "liquidez_dias": 90,
        "preco_referencia": {"autografada": 1800, "match_worn": 5500, "retro": 450},
        "copa_2026": True, "controversias_ativas": [],
        "eventos_futuros": [
            {"descricao": "Copa do Mundo 2026", "data": date(2026, 6, 11), "boost": 20},
        ],
        "tags": ["santos", "barcelona", "psg", "brasil", "copa26"],
    },

    "dani_alves": {
        "nomes_busca": ["Dani Alves", "Daniel Alves", "Daniel Alves da Silva"],
        "clubes": ["Barcelona", "Juventus", "PSG", "Brasil"],
        "pais": "BR", "esporte": "football",
        "raridade": "rare", "liquidez_dias": 100,
        "preco_referencia": {"autografada": 1200, "match_worn": 3500, "retro": 350},
        "copa_2026": False, "controversias_ativas": ["Caso judicial 2023 (encerrado)"],
        "eventos_futuros": [],
        "tags": ["barcelona", "brasil"],
    },

    "thiago_silva": {
        "nomes_busca": ["Thiago Silva", "Thiago Silva Ferreira", "O Monstro"],
        "clubes": ["Milan", "PSG", "Chelsea", "Brasil"],
        "pais": "BR", "esporte": "football",
        "raridade": "rare", "liquidez_dias": 100,
        "preco_referencia": {"autografada": 1200, "match_worn": 3500, "retro": 350},
        "copa_2026": False, "controversias_ativas": [],
        "eventos_futuros": [],
        "tags": ["psg", "chelsea", "brasil"],
    },

    "vinicius_jr": {
        "nomes_busca": ["Vinicius Jr", "Vini Jr", "Vinícius Júnior", "Vinicius Junior"],
        "clubes": ["Flamengo", "Real Madrid", "Brasil"],
        "pais": "BR", "esporte": "football",
        "raridade": "rare", "liquidez_dias": 60,
        "preco_referencia": {"autografada": 2200, "match_worn": 6000, "retro": 500},
        "copa_2026": True, "controversias_ativas": [],
        "eventos_futuros": [
            {"descricao": "Copa do Mundo 2026", "data": date(2026, 6, 11), "boost": 20},
        ],
        "tags": ["real_madrid", "brasil", "copa26", "champions"],
    },

    "gabriel_martinelli": {
        "nomes_busca": ["Gabriel Martinelli", "Martinelli", "Gabriel Silva Martinelli"],
        "clubes": ["Arsenal", "Brasil"],
        "pais": "BR", "esporte": "football",
        "raridade": "rare", "liquidez_dias": 75,
        "preco_referencia": {"autografada": 2690, "match_worn": 6000, "retro": 500},
        "copa_2026": True, "controversias_ativas": [],
        "eventos_futuros": [
            {"descricao": "Copa do Mundo 2026", "data": date(2026, 6, 11), "boost": 15},
        ],
        "tags": ["arsenal", "brasil", "copa26"],
    },

    "dunga": {
        "nomes_busca": ["Dunga", "Carlos Caetano Bledorn Verri"],
        "clubes": ["Internacional", "Stuttgart", "Jubilo Iwata", "Brasil"],
        "pais": "BR", "esporte": "football",
        "raridade": "rare", "liquidez_dias": 90,
        "preco_referencia": {"autografada": 1500, "match_worn": 4000, "retro": 400},
        "copa_2026": False, "controversias_ativas": [],
        "eventos_futuros": [],
        "tags": ["internacional", "brasil", "copa94"],
    },

    # ─────────────────────────────────────────────────────────────────────────
    # FUTEBOL — ARGENTINA
    # ─────────────────────────────────────────────────────────────────────────

    "maradona": {
        "nomes_busca": ["Maradona", "Diego Maradona", "Diego Armando Maradona", "El Pibe de Oro", "El Diego"],
        "clubes": ["Boca Juniors", "Barcelona", "Napoli", "Argentina"],
        "pais": "AR", "esporte": "football",
        "raridade": "icon", "liquidez_dias": 10,
        "preco_referencia": {"autografada": 15000, "match_worn": 40000, "retro": 3000},
        "copa_2026": False, "controversias_ativas": [],
        "eventos_futuros": [
            {"descricao": "5 anos do falecimento", "data": date(2025, 11, 25), "boost": 15},
            {"descricao": "40 anos gol da mão de Deus", "data": date(2026, 6, 22), "boost": 20},
        ],
        "tags": ["boca", "napoli", "argentina", "copa86", "pibe_de_oro", "icon"],
    },

    "messi": {
        "nomes_busca": ["Messi", "Leo Messi", "Lionel Messi", "La Pulga", "Lionel Andrés Messi"],
        "clubes": ["Barcelona", "PSG", "Inter Miami", "Argentina"],
        "pais": "AR", "esporte": "football",
        "raridade": "icon", "liquidez_dias": 12,
        "preco_referencia": {"autografada": 8000, "match_worn": 30000, "retro": 2000},
        "copa_2026": True, "controversias_ativas": [],
        "eventos_futuros": [
            {"descricao": "Copa do Mundo 2026 (última Copa esperada)", "data": date(2026, 6, 11), "boost": 25},
        ],
        "tags": ["barcelona", "psg", "inter_miami", "argentina", "copa22", "pulga", "icon"],
    },

    "batistuta": {
        "nomes_busca": ["Batistuta", "Gabriel Batistuta", "Batigol", "Gabriel Omar Batistuta"],
        "clubes": ["Fiorentina", "Roma", "Argentina"],
        "pais": "AR", "esporte": "football",
        "raridade": "legend", "liquidez_dias": 45,
        "preco_referencia": {"autografada": 2690, "match_worn": 7500, "retro": 600},
        "copa_2026": False, "controversias_ativas": [],
        "eventos_futuros": [],
        "tags": ["fiorentina", "roma", "argentina", "batigol"],
    },

    "riquelme": {
        "nomes_busca": ["Riquelme", "Juan Román Riquelme", "JRR", "Juan Roman Riquelme"],
        "clubes": ["Boca Juniors", "Barcelona", "Villarreal", "Argentina"],
        "pais": "AR", "esporte": "football",
        "raridade": "legend", "liquidez_dias": 40,
        "preco_referencia": {"autografada": 2500, "match_worn": 7000, "retro": 550},
        "copa_2026": False, "controversias_ativas": [],
        "eventos_futuros": [],
        "tags": ["boca", "villarreal", "argentina"],
    },

    "kempes": {
        "nomes_busca": ["Kempes", "Mario Kempes", "El Matador", "Mario Alberto Kempes"],
        "clubes": ["Valencia", "Argentina"],
        "pais": "AR", "esporte": "football",
        "raridade": "legend", "liquidez_dias": 60,
        "preco_referencia": {"autografada": 2200, "match_worn": 8000, "retro": 700},
        "copa_2026": False, "controversias_ativas": [],
        "eventos_futuros": [],
        "tags": ["valencia", "argentina", "copa78", "matador"],
    },

    "caniggia": {
        "nomes_busca": ["Caniggia", "Claudio Caniggia", "El Hijo del Viento"],
        "clubes": ["River Plate", "Atalanta", "Roma", "Argentina"],
        "pais": "AR", "esporte": "football",
        "raridade": "rare", "liquidez_dias": 80,
        "preco_referencia": {"autografada": 1800, "match_worn": 5000, "retro": 450},
        "copa_2026": False, "controversias_ativas": [],
        "eventos_futuros": [],
        "tags": ["river", "roma", "argentina"],
    },

    "zanetti": {
        "nomes_busca": ["Zanetti", "Javier Zanetti", "El Tractor"],
        "clubes": ["Inter Milan", "Argentina"],
        "pais": "AR", "esporte": "football",
        "raridade": "legend", "liquidez_dias": 50,
        "preco_referencia": {"autografada": 2000, "match_worn": 5500, "retro": 500},
        "copa_2026": False, "controversias_ativas": [],
        "eventos_futuros": [],
        "tags": ["inter_milan", "argentina", "trator"],
    },

    "tevez": {
        "nomes_busca": ["Tevez", "Carlos Tevez", "Carlitos", "Apache"],
        "clubes": ["Boca Juniors", "West Ham", "Manchester United", "Manchester City", "Juventus", "Argentina"],
        "pais": "AR", "esporte": "football",
        "raridade": "rare", "liquidez_dias": 70,
        "preco_referencia": {"autografada": 1600, "match_worn": 4500, "retro": 420},
        "copa_2026": False, "controversias_ativas": [],
        "eventos_futuros": [],
        "tags": ["boca", "manchester", "juventus", "argentina"],
    },

    "aguero": {
        "nomes_busca": ["Agüero", "Aguero", "Kun Agüero", "Sergio Agüero", "Kun Aguero"],
        "clubes": ["Atlético Madrid", "Manchester City", "Barcelona", "Argentina"],
        "pais": "AR", "esporte": "football",
        "raridade": "legend", "liquidez_dias": 40,
        "preco_referencia": {"autografada": 2690, "match_worn": 7000, "retro": 600},
        "copa_2026": False, "controversias_ativas": [],
        "eventos_futuros": [],
        "tags": ["manchester_city", "argentina", "kun"],
    },

    "di_maria": {
        "nomes_busca": ["Di María", "Di Maria", "Ángel Di María", "El Fideo"],
        "clubes": ["Benfica", "Real Madrid", "Manchester United", "PSG", "Juventus", "Argentina"],
        "pais": "AR", "esporte": "football",
        "raridade": "rare", "liquidez_dias": 70,
        "preco_referencia": {"autografada": 1800, "match_worn": 5000, "retro": 450},
        "copa_2026": False, "controversias_ativas": [],
        "eventos_futuros": [],
        "tags": ["psg", "real_madrid", "argentina", "copa22", "fideo"],
    },

    "crespo": {
        "nomes_busca": ["Crespo", "Hernán Crespo", "Hernan Crespo", "El Valdanito"],
        "clubes": ["Lazio", "Inter Milan", "Chelsea", "Milan", "Argentina"],
        "pais": "AR", "esporte": "football",
        "raridade": "rare", "liquidez_dias": 90,
        "preco_referencia": {"autografada": 2690, "match_worn": 6000, "retro": 550},
        "copa_2026": False, "controversias_ativas": [],
        "eventos_futuros": [],
        "tags": ["chelsea", "inter_milan", "argentina"],
    },

    "mascherano": {
        "nomes_busca": ["Mascherano", "Javier Mascherano", "El Jefecito"],
        "clubes": ["Boca Juniors", "Liverpool", "Barcelona", "Argentina"],
        "pais": "AR", "esporte": "football",
        "raridade": "rare", "liquidez_dias": 90,
        "preco_referencia": {"autografada": 2200, "match_worn": 6000, "retro": 500},
        "copa_2026": False, "controversias_ativas": [],
        "eventos_futuros": [],
        "tags": ["barcelona", "liverpool", "argentina"],
    },

    "veron": {
        "nomes_busca": ["Verón", "Veron", "Juan Sebastián Verón", "La Brujita"],
        "clubes": ["Lazio", "Manchester United", "Chelsea", "Inter", "Argentina"],
        "pais": "AR", "esporte": "football",
        "raridade": "rare", "liquidez_dias": 100,
        "preco_referencia": {"autografada": 1500, "match_worn": 4000, "retro": 400},
        "copa_2026": False, "controversias_ativas": [],
        "eventos_futuros": [],
        "tags": ["lazio", "manchester_united", "argentina"],
    },

    "higuain": {
        "nomes_busca": ["Higuaín", "Higuain", "Gonzalo Higuaín", "Pipita"],
        "clubes": ["Real Madrid", "Napoli", "Juventus", "Milan", "Argentina"],
        "pais": "AR", "esporte": "football",
        "raridade": "rare", "liquidez_dias": 90,
        "preco_referencia": {"autografada": 1500, "match_worn": 4000, "retro": 380},
        "copa_2026": False, "controversias_ativas": [],
        "eventos_futuros": [],
        "tags": ["napoli", "juventus", "argentina", "pipita"],
    },

    "lautaro": {
        "nomes_busca": ["Lautaro Martínez", "Lautaro Martinez", "El Toro"],
        "clubes": ["Inter Milan", "Argentina"],
        "pais": "AR", "esporte": "football",
        "raridade": "rare", "liquidez_dias": 65,
        "preco_referencia": {"autografada": 2000, "match_worn": 5500, "retro": 480},
        "copa_2026": True, "controversias_ativas": [],
        "eventos_futuros": [
            {"descricao": "Copa do Mundo 2026", "data": date(2026, 6, 11), "boost": 15},
        ],
        "tags": ["inter_milan", "argentina", "copa26", "toro"],
    },

    # ─────────────────────────────────────────────────────────────────────────
    # FUTEBOL — EUROPA (ITÁLIA)
    # ─────────────────────────────────────────────────────────────────────────

    "totti": {
        "nomes_busca": ["Totti", "Francesco Totti", "Il Capitano", "Er Pupone"],
        "clubes": ["Roma", "Itália"],
        "pais": "IT", "esporte": "football",
        "raridade": "legend", "liquidez_dias": 40,
        "preco_referencia": {"autografada": 2790, "match_worn": 8000, "retro": 650},
        "copa_2026": False, "controversias_ativas": [],
        "eventos_futuros": [],
        "tags": ["roma", "italia", "capitano"],
    },

    "maldini": {
        "nomes_busca": ["Maldini", "Paolo Maldini", "Paolo Cesare Maldini"],
        "clubes": ["AC Milan", "Itália"],
        "pais": "IT", "esporte": "football",
        "raridade": "legend", "liquidez_dias": 35,
        "preco_referencia": {"autografada": 3200, "match_worn": 9000, "retro": 700},
        "copa_2026": False, "controversias_ativas": [],
        "eventos_futuros": [],
        "tags": ["milan", "italia", "capitano"],
    },

    "del_piero": {
        "nomes_busca": ["Del Piero", "Alessandro Del Piero", "Alex Del Piero", "Pinturicchio"],
        "clubes": ["Juventus", "Itália"],
        "pais": "IT", "esporte": "football",
        "raridade": "legend", "liquidez_dias": 45,
        "preco_referencia": {"autografada": 2800, "match_worn": 8000, "retro": 650},
        "copa_2026": False, "controversias_ativas": [],
        "eventos_futuros": [],
        "tags": ["juventus", "italia", "pinturicchio"],
    },

    "buffon": {
        "nomes_busca": ["Buffon", "Gianluigi Buffon", "Super Gigi"],
        "clubes": ["Juventus", "PSG", "Parma", "Itália"],
        "pais": "IT", "esporte": "football",
        "raridade": "legend", "liquidez_dias": 55,
        "preco_referencia": {"autografada": 2500, "match_worn": 7000, "retro": 580},
        "copa_2026": False, "controversias_ativas": [],
        "eventos_futuros": [],
        "tags": ["juventus", "italia"],
    },

    "baggio": {
        "nomes_busca": ["Baggio", "Roberto Baggio", "Il Divin Codino", "Robert Baggio"],
        "clubes": ["Fiorentina", "Juventus", "Milan", "Itália"],
        "pais": "IT", "esporte": "football",
        "raridade": "legend", "liquidez_dias": 40,
        "preco_referencia": {"autografada": 3000, "match_worn": 9000, "retro": 700},
        "copa_2026": False, "controversias_ativas": [],
        "eventos_futuros": [],
        "tags": ["juventus", "milan", "fiorentina", "italia", "copa94"],
    },

    "inzaghi": {
        "nomes_busca": ["Inzaghi", "Filippo Inzaghi", "Pippo Inzaghi", "Super Pippo"],
        "clubes": ["AC Milan", "Juventus", "Itália"],
        "pais": "IT", "esporte": "football",
        "raridade": "rare", "liquidez_dias": 90,
        "preco_referencia": {"autografada": 2000, "match_worn": 5500, "retro": 500},
        "copa_2026": False, "controversias_ativas": [],
        "eventos_futuros": [],
        "tags": ["milan", "juventus", "italia"],
    },

    "cannavaro": {
        "nomes_busca": ["Cannavaro", "Fabio Cannavaro", "Fabio Cannavaro Napoli"],
        "clubes": ["Napoli", "Parma", "Inter", "Juventus", "Real Madrid", "Itália"],
        "pais": "IT", "esporte": "football",
        "raridade": "rare", "liquidez_dias": 85,
        "preco_referencia": {"autografada": 2990, "match_worn": 7000, "retro": 600},
        "copa_2026": False, "controversias_ativas": [],
        "eventos_futuros": [],
        "tags": ["real_madrid", "juventus", "italia", "copa06"],
    },

    "shevchenko": {
        "nomes_busca": ["Shevchenko", "Andriy Shevchenko", "Andrei Shevchenko", "Sheva"],
        "clubes": ["Dynamo Kyiv", "AC Milan", "Chelsea", "Ucrânia"],
        "pais": "UA", "esporte": "football",
        "raridade": "legend", "liquidez_dias": 50,
        "preco_referencia": {"autografada": 2500, "match_worn": 7000, "retro": 580},
        "copa_2026": False, "controversias_ativas": [],
        "eventos_futuros": [],
        "tags": ["milan", "chelsea", "ucrania", "bola_de_ouro"],
    },

    "seedorf": {
        "nomes_busca": ["Seedorf", "Clarence Seedorf"],
        "clubes": ["Ajax", "Real Madrid", "Inter", "AC Milan", "Holanda"],
        "pais": "NL", "esporte": "football",
        "raridade": "rare", "liquidez_dias": 90,
        "preco_referencia": {"autografada": 2690, "match_worn": 6500, "retro": 550},
        "copa_2026": False, "controversias_ativas": [],
        "eventos_futuros": [],
        "tags": ["milan", "real_madrid", "holanda"],
    },

    # ─────────────────────────────────────────────────────────────────────────
    # FUTEBOL — HOLANDA / BÉLGICA
    # ─────────────────────────────────────────────────────────────────────────

    "van_basten": {
        "nomes_busca": ["Van Basten", "Marco van Basten", "Marco Van Basten"],
        "clubes": ["Ajax", "AC Milan", "Holanda"],
        "pais": "NL", "esporte": "football",
        "raridade": "legend", "liquidez_dias": 40,
        "preco_referencia": {"autografada": 3000, "match_worn": 9000, "retro": 700},
        "copa_2026": False, "controversias_ativas": [],
        "eventos_futuros": [],
        "tags": ["milan", "ajax", "holanda", "bola_de_ouro"],
    },

    "gullit": {
        "nomes_busca": ["Gullit", "Ruud Gullit", "Ruud Gullit Rotterdam"],
        "clubes": ["Feyenoord", "AC Milan", "Holanda"],
        "pais": "NL", "esporte": "football",
        "raridade": "legend", "liquidez_dias": 50,
        "preco_referencia": {"autografada": 2800, "match_worn": 8000, "retro": 650},
        "copa_2026": False, "controversias_ativas": [],
        "eventos_futuros": [],
        "tags": ["milan", "holanda", "bola_de_ouro"],
    },

    "kluivert": {
        "nomes_busca": ["Kluivert", "Patrick Kluivert", "Patrick Stephan Kluivert"],
        "clubes": ["Ajax", "Barcelona", "Milan", "Holanda"],
        "pais": "NL", "esporte": "football",
        "raridade": "rare", "liquidez_dias": 90,
        "preco_referencia": {"autografada": 2690, "match_worn": 6500, "retro": 550},
        "copa_2026": False, "controversias_ativas": [],
        "eventos_futuros": [],
        "tags": ["barcelona", "ajax", "holanda"],
    },

    # ─────────────────────────────────────────────────────────────────────────
    # FUTEBOL — ESPANHA
    # ─────────────────────────────────────────────────────────────────────────

    "raul": {
        "nomes_busca": ["Raúl", "Raul", "Raúl González", "Raul Gonzalez"],
        "clubes": ["Real Madrid", "Schalke", "Espanha"],
        "pais": "ES", "esporte": "football",
        "raridade": "legend", "liquidez_dias": 50,
        "preco_referencia": {"autografada": 2500, "match_worn": 7000, "retro": 580},
        "copa_2026": False, "controversias_ativas": [],
        "eventos_futuros": [],
        "tags": ["real_madrid", "espanha"],
    },

    "iniesta": {
        "nomes_busca": ["Iniesta", "Andrés Iniesta", "Andres Iniesta", "El Ilusionista"],
        "clubes": ["Barcelona", "Vissel Kobe", "Espanha"],
        "pais": "ES", "esporte": "football",
        "raridade": "legend", "liquidez_dias": 45,
        "preco_referencia": {"autografada": 2800, "match_worn": 7500, "retro": 620},
        "copa_2026": False, "controversias_ativas": [],
        "eventos_futuros": [],
        "tags": ["barcelona", "espanha", "copa10"],
    },

    "xavi": {
        "nomes_busca": ["Xavi", "Xavi Hernández", "Xavi Hernandez"],
        "clubes": ["Barcelona", "Al-Sadd", "Espanha"],
        "pais": "ES", "esporte": "football",
        "raridade": "legend", "liquidez_dias": 50,
        "preco_referencia": {"autografada": 2500, "match_worn": 7000, "retro": 580},
        "copa_2026": False, "controversias_ativas": [],
        "eventos_futuros": [],
        "tags": ["barcelona", "espanha", "copa10"],
    },

    # ─────────────────────────────────────────────────────────────────────────
    # FUTEBOL — PORTUGAL
    # ─────────────────────────────────────────────────────────────────────────

    "figo": {
        "nomes_busca": ["Figo", "Luís Figo", "Luis Figo", "Luis Filipe Madeira de Faria Figo"],
        "clubes": ["Barcelona", "Real Madrid", "Inter", "Portugal"],
        "pais": "PT", "esporte": "football",
        "raridade": "legend", "liquidez_dias": 50,
        "preco_referencia": {"autografada": 2800, "match_worn": 7500, "retro": 620},
        "copa_2026": False, "controversias_ativas": [],
        "eventos_futuros": [],
        "tags": ["real_madrid", "barcelona", "portugal", "bola_de_ouro"],
    },

    "ronaldo_cr7": {
        "nomes_busca": ["Cristiano Ronaldo", "CR7", "CR 7", "Cristiano Ronaldo dos Santos Aveiro"],
        "clubes": ["Manchester United", "Real Madrid", "Juventus", "Al-Nassr", "Portugal"],
        "pais": "PT", "esporte": "football",
        "raridade": "icon", "liquidez_dias": 15,
        "preco_referencia": {"autografada": 6000, "match_worn": 20000, "retro": 1500},
        "copa_2026": True, "controversias_ativas": [],
        "eventos_futuros": [
            {"descricao": "Copa do Mundo 2026 (provavelmente última)", "data": date(2026, 6, 11), "boost": 22},
        ],
        "tags": ["real_madrid", "manchester", "juve", "portugal", "cr7", "icon"],
    },

    # ─────────────────────────────────────────────────────────────────────────
    # FUTEBOL — Inglaterra
    # ─────────────────────────────────────────────────────────────────────────

    "beckham": {
        "nomes_busca": ["Beckham", "David Beckham", "Golden Balls"],
        "clubes": ["Manchester United", "Real Madrid", "LA Galaxy", "PSG", "Inter Miami", "Inglaterra"],
        "pais": "EN", "esporte": "football",
        "raridade": "legend", "liquidez_dias": 35,
        "preco_referencia": {"autografada": 2800, "match_worn": 8000, "retro": 650},
        "copa_2026": False, "controversias_ativas": [],
        "eventos_futuros": [],
        "tags": ["manchester_united", "real_madrid", "ingles"],
    },

    "gerrard": {
        "nomes_busca": ["Gerrard", "Steven Gerrard", "Steve Gerrard"],
        "clubes": ["Liverpool", "LA Galaxy", "Inglaterra"],
        "pais": "EN", "esporte": "football",
        "raridade": "legend", "liquidez_dias": 50,
        "preco_referencia": {"autografada": 2200, "match_worn": 6500, "retro": 550},
        "copa_2026": False, "controversias_ativas": [],
        "eventos_futuros": [],
        "tags": ["liverpool", "ingles"],
    },

    "rooney": {
        "nomes_busca": ["Rooney", "Wayne Rooney", "Wazza"],
        "clubes": ["Manchester United", "Everton", "Inglaterra"],
        "pais": "EN", "esporte": "football",
        "raridade": "rare", "liquidez_dias": 80,
        "preco_referencia": {"autografada": 2000, "match_worn": 5500, "retro": 480},
        "copa_2026": False, "controversias_ativas": [],
        "eventos_futuros": [],
        "tags": ["manchester_united", "ingles"],
    },

    "bale": {
        "nomes_busca": ["Bale", "Gareth Bale", "Gareth Frank Bale"],
        "clubes": ["Tottenham", "Real Madrid", "LA FC", "País de Gales"],
        "pais": "WA", "esporte": "football",
        "raridade": "rare", "liquidez_dias": 75,
        "preco_referencia": {"autografada": 3790, "match_worn": 8500, "retro": 700},
        "copa_2026": False, "controversias_ativas": [],
        "eventos_futuros": [],
        "tags": ["real_madrid", "tottenham"],
    },

    # ─────────────────────────────────────────────────────────────────────────
    # FUTEBOL — OUTROS
    # ─────────────────────────────────────────────────────────────────────────

    "suarez": {
        "nomes_busca": ["Suárez", "Suarez", "Luis Suárez", "Luis Suarez", "El Pistolero"],
        "clubes": ["Liverpool", "Barcelona", "Atlético Madrid", "Uruguai"],
        "pais": "UY", "esporte": "football",
        "raridade": "rare", "liquidez_dias": 70,
        "preco_referencia": {"autografada": 2690, "match_worn": 7000, "retro": 580},
        "copa_2026": False, "controversias_ativas": [],
        "eventos_futuros": [],
        "tags": ["liverpool", "barcelona", "uruguai"],
    },

    "torres": {
        "nomes_busca": ["Torres", "Fernando Torres", "El Niño"],
        "clubes": ["Liverpool", "Chelsea", "Atlético Madrid", "Espanha"],
        "pais": "ES", "esporte": "football",
        "raridade": "rare", "liquidez_dias": 85,
        "preco_referencia": {"autografada": 2690, "match_worn": 6500, "retro": 550},
        "copa_2026": False, "controversias_ativas": [],
        "eventos_futuros": [],
        "tags": ["liverpool", "chelsea", "espanha"],
    },

    "drogba": {
        "nomes_busca": ["Drogba", "Didier Drogba", "Didier Yves Drogba Tébily"],
        "clubes": ["Chelsea", "Galatasaray", "Costa do Marfim"],
        "pais": "CI", "esporte": "football",
        "raridade": "legend", "liquidez_dias": 55,
        "preco_referencia": {"autografada": 2500, "match_worn": 7000, "retro": 580},
        "copa_2026": False, "controversias_ativas": [],
        "eventos_futuros": [],
        "tags": ["chelsea", "costa_do_marfim"],
    },

    "higuita": {
        "nomes_busca": ["Higuita", "René Higuita", "Rene Higuita", "El Loco"],
        "clubes": ["Atlético Nacional", "Colômbia"],
        "pais": "CO", "esporte": "football",
        "raridade": "rare", "liquidez_dias": 80,
        "preco_referencia": {"autografada": 3690, "match_worn": 8000, "retro": 700},
        "copa_2026": False, "controversias_ativas": [],
        "eventos_futuros": [],
        "tags": ["colombia", "el_loco", "escorpiao"],
    },

    "ballack": {
        "nomes_busca": ["Ballack", "Michael Ballack", "Der Chef"],
        "clubes": ["Bayern Munich", "Chelsea", "Bayer Leverkusen", "Alemanha"],
        "pais": "DE", "esporte": "football",
        "raridade": "legend", "liquidez_dias": 60,
        "preco_referencia": {"autografada": 3990, "match_worn": 9000, "retro": 750},
        "copa_2026": False, "controversias_ativas": [],
        "eventos_futuros": [],
        "tags": ["chelsea", "bayern", "alemanha"],
    },

    # ─────────────────────────────────────────────────────────────────────────
    # F1 — MANTER NO BANCO PARA REFERÊNCIA DE PREÇO
    # (Itens F1 são filtrados nos scrapers, mas se aparecerem camisa/uniforme
    # autografado o score engine precisa saber o valor correto)
    # ─────────────────────────────────────────────────────────────────────────

    "senna": {
        "nomes_busca": ["Senna", "Ayrton Senna", "Ayrton Senna da Silva", "Magic"],
        "clubes": ["McLaren", "Lotus", "Williams", "Toleman", "Brasil"],
        "pais": "BR", "esporte": "f1",
        "raridade": "icon", "liquidez_dias": 10,
        "preco_referencia": {"autografada": 30000, "match_worn": 80000, "retro": 5000},
        "copa_2026": False, "controversias_ativas": [],
        "eventos_futuros": [
            {"descricao": "30 anos do falecimento (Imola)", "data": date(2024, 5, 1), "boost": 25},
            {"descricao": "35 anos do falecimento", "data": date(2029, 5, 1), "boost": 20},
        ],
        "tags": ["mclaren", "brasil", "f1", "magic", "icon"],
    },

}

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def find_player(title: str, extracted_name: str = "") -> dict | None:
    """Retorna dados do jogador se encontrado no título ou nome extraído."""
    search_text = f"{title} {extracted_name}".lower()
    for key, data in PLAYERS.items():
        for name in data.get("nomes_busca", []):
            if name.lower() in search_text:
                return data
    return None


def get_player_or_default(title: str, extracted_name: str = "") -> dict:
    """Retorna dados do jogador ou defaults para item sem jogador identificado."""
    player = find_player(title, extracted_name)
    if player:
        return player
    return {
        "raridade": "regional",
        "liquidez_dias": 180,
        "preco_referencia": {"autografada": 800, "match_worn": 1500, "retro": 300},
        "eventos_futuros": [],
        "copa_2026": False,
        "controversias_ativas": [],
        "tags": [],
    }


PRIORITY_CLUBS = [
    "Flamengo", "Santos", "Corinthians", "Palmeiras", "Vasco", "São Paulo",
    "Grêmio", "Internacional", "Atlético Mineiro", "Botafogo", "Cruzeiro",
    "Boca Juniors", "River Plate",
    "Real Madrid", "Barcelona", "Manchester United", "Liverpool", "Arsenal",
    "Inter Milan", "Juventus", "AC Milan", "Bayern Munich", "PSG", "Chelsea",
    "Napoli", "Roma", "Fiorentina", "Lazio",
    "Brasil", "Argentina", "Portugal", "França", "Itália", "Espanha", "Holanda",
]

POSITIVE_KEYWORDS = [
    "autografada", "autografado", "autógrafo", "autografo",
    "assinada", "assinado", "assinatura",
    "autografiada", "autografiado", "firmada", "firmado",
    "match worn", "jogo", "usada em jogo", "usada en partido",
    "original", "certificado", "certificado de autenticidade",
    "certificado de autenticidad",
    "COA", "PSA", "Beckett", "JSA", "SB Brasil", "Fabricks",
    "match issued", "player issue", "player edition",
    "edição limitada", "edicion limitada", "numerada",
]

NEGATIVE_KEYWORDS = [
    "réplica", "replica", "tailandesa", "tailandês",
    "inspirada", "inspirado", "similar", "cópia", "copia",
    "fake", "imitação", "imitacao", "imitacion",
    "não autografad", "sem autografo",
]
