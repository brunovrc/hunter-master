"""
Catálogo de camisas originais do estoque pessoal do operador.

Fonte: planilha "CATÁLOGO DE CAMISAS ORIGINAIS — ESTOQUE COMPLETO" (49 peças)
Usado pelo agente para:
  1. Calibrar estimativas de preço de revenda para camisas vintage/retro
  2. Identificar quando um anúncio é de item semelhante ao estoque (oportunidade ou concorrente)
  3. Enriquecer o contexto de SPORTS_CONTEXT com clubes/eras específicas
  4. Treinar o score engine para reconhecer raridade real vs percebida

Tags de raridade:
  JOIA           — peça de alto valor histórico/visual, difícil de achar
  JOIA+ASSINADA  — joia + assinatura real (máxima raridade)
  RARO           — aparece com pouca frequência no mercado
  (sem tag)      — camisa original comum, boa condição
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class CatalogJersey:
    lote: int
    clube: str
    liga: str
    pais: str
    marca: str
    tipo: str           # home / away / third / gk / centenario / retro / etc.
    periodo: str        # "2019-20", "1996-97", "1998" etc.
    patrocinador: str
    conservacao: str    # "Excelente", "Boa", "Boa (desgaste leve)"
    tag: str            # "JOIA", "JOIA+ASSINADA", "RARO", ""
    vl_min: float       # BRL
    vl_max: float       # BRL
    contexto: str       # observações históricas relevantes

    @property
    def vl_medio(self) -> float:
        return (self.vl_min + self.vl_max) / 2

    @property
    def is_joia(self) -> bool:
        return "JOIA" in self.tag

    @property
    def is_assinada(self) -> bool:
        return "ASSINADA" in self.tag

    @property
    def is_raro(self) -> bool:
        return self.tag in ("RARO",) or self.is_joia


# ── CATÁLOGO COMPLETO ──────────────────────────────────────────────────────────

CATALOG: list[CatalogJersey] = [

    # ── Lote 1-10 ─────────────────────────────────────────────────────────────

    CatalogJersey(
        lote=1, clube="Rangers FC", liga="Scottish Premiership", pais="Escócia",
        marca="Puma", tipo="home", periodo="2012-13", patrocinador="Tennent's",
        conservacao="Excelente", tag="RARO", vl_min=280, vl_max=420,
        contexto=(
            "Rangers rebaixou para a 4ª divisão escocesa em 2012 por falência. "
            "Esta é a última camisa antes do colapso — colecionada pela raridade histórica."
        ),
    ),

    CatalogJersey(
        lote=2, clube="AS Roma", liga="Serie A", pais="Itália",
        marca="Nike", tipo="third", periodo="2019-20", patrocinador="Qatar Airways",
        conservacao="Excelente", tag="", vl_min=300, vl_max=450,
        contexto=(
            "Camisa third da Roma temporada pré-pandemia. Design em marrom fosco atípico "
            "para a Serie A, muito procurada por colecionadores do futebol italiano."
        ),
    ),

    CatalogJersey(
        lote=3, clube="Inter de Milão", liga="Serie A", pais="Itália",
        marca="Nike", tipo="away", periodo="2014-15", patrocinador="Pirelli",
        conservacao="Excelente", tag="", vl_min=280, vl_max=400,
        contexto=(
            "Away branca da Inter na era pós-Mourinho. Pirelli como patrocinador histórico "
            "desde 1995. Boa liquidez entre colecionadores italianos."
        ),
    ),

    CatalogJersey(
        lote=4, clube="Manchester United", liga="Premier League", pais="Inglaterra",
        marca="Adidas", tipo="away", periodo="2015-16", patrocinador="Chevrolet",
        conservacao="Excelente", tag="", vl_min=350, vl_max=500,
        contexto=(
            "Away azul do United na era Van Gaal. Adidas retornou ao clube em 2015. "
            "Primeira temporada completa da parceria Adidas-MUFC."
        ),
    ),

    CatalogJersey(
        lote=5, clube="Universitario de Deportes", liga="Liga 1 Peru", pais="Peru",
        marca="Umbro", tipo="away", periodo="2019", patrocinador="Gloria",
        conservacao="Excelente", tag="RARO", vl_min=180, vl_max=300,
        contexto=(
            "Away azul escuro do maior clube do Peru. Raridade no mercado brasileiro — "
            "praticamente inexistente fora do circuito peruano."
        ),
    ),

    CatalogJersey(
        lote=6, clube="Boca Juniors", liga="Primera División", pais="Argentina",
        marca="Nike", tipo="home", periodo="2015", patrocinador="Quilmes",
        conservacao="Excelente", tag="", vl_min=350, vl_max=550,
        contexto=(
            "Camisa do centenário da fundação do Boca Juniors (1905-2005, lançada em "
            "comemoração ao 110º). Alta demanda entre colecionadores argentinos e brasileiros."
        ),
    ),

    CatalogJersey(
        lote=7, clube="Seleção Brasileira", liga="Internacional", pais="Brasil",
        marca="Nike", tipo="away", periodo="2019", patrocinador="",
        conservacao="Excelente", tag="", vl_min=350, vl_max=500,
        contexto=(
            "Away azul da Seleção, temporada Copa América 2019 (vencida pelo Brasil). "
            "Gerada imediatamente antes da pandemia — boa liquidez no mercado nacional."
        ),
    ),

    CatalogJersey(
        lote=8, clube="Seleção Brasileira", liga="Internacional", pais="Brasil",
        marca="Nike", tipo="home", periodo="1998", patrocinador="",
        conservacao="Excelente", tag="JOIA", vl_min=700, vl_max=1200,
        contexto=(
            "Camisa #10 da Copa do Mundo França 1998 — Ronaldo Fenômeno teve a crise "
            "misteriosa antes da final. Uma das camisas mais icônicas da história. "
            "Alta liquidez entre colecionadores de Ronaldo e da era ouro brasileira."
        ),
    ),

    CatalogJersey(
        lote=9, clube="Everton FC", liga="Premier League", pais="Inglaterra",
        marca="Umbro", tipo="home", periodo="2018-19", patrocinador="SportPesa",
        conservacao="Excelente", tag="JOIA+ASSINADA", vl_min=600, vl_max=1200,
        contexto=(
            "Camisa assinada por todo o elenco 2018-19. Inclui assinaturas de Jordan Pickford, "
            "Richarlison, Bernard entre outros. COA informal (foto com jogadores). "
            "Raridade absoluta no mercado brasileiro."
        ),
    ),

    CatalogJersey(
        lote=10, clube="PSG", liga="Ligue 1", pais="França",
        marca="Nike x Jordan", tipo="third", periodo="2018-19", patrocinador="Fly Emirates",
        conservacao="Excelente", tag="RARO", vl_min=500, vl_max=800,
        contexto=(
            "Collab Nike x Jordan Brand — primeira coleção third do PSG com branding Jordan. "
            "Neymar Jr. usou nesta temporada. Uma das camisas mais desejadas do futebol moderno."
        ),
    ),

    # ── Lote 11-20 ────────────────────────────────────────────────────────────

    CatalogJersey(
        lote=11, clube="Inter de Milão", liga="Serie A", pais="Itália",
        marca="Umbro", tipo="home", periodo="1996-97", patrocinador="Pirelli",
        conservacao="Excelente", tag="RARO", vl_min=580, vl_max=920,
        contexto=(
            "Era Ronaldo Fenômeno na Inter — temporada 1997-98 foi a melhor de R9. "
            "Camisa Umbro azul-preta clássica. Muito procurada por colecionadores de Ronaldo. "
            "Pirelli histórico. Alta liquidez."
        ),
    ),

    CatalogJersey(
        lote=12, clube="AS Roma", liga="Serie A", pais="Itália",
        marca="Kappa", tipo="home", periodo="2000-01", patrocinador="ITAS",
        conservacao="Excelente", tag="RARO", vl_min=520, vl_max=840,
        contexto=(
            "Camisa do único scudetto da Roma no século XXI (2000-01). "
            "Totti, Batistuta e Cafu no elenco. Kappa como fornecedora. "
            "Item de alta demanda entre colecionadores italianos e de Batistuta."
        ),
    ),

    CatalogJersey(
        lote=13, clube="FC Barcelona", liga="La Liga", pais="Espanha",
        marca="Nike", tipo="away", periodo="2011-12", patrocinador="Qatar Foundation",
        conservacao="Excelente", tag="RARO", vl_min=430, vl_max=670,
        contexto=(
            "Away amarela da era Pep Guardiola — equipe considerada a melhor de todos os tempos. "
            "Qatar Foundation como patrocinador (antes Qatar Airways). Messi, Xavi, Iniesta. "
            "Muito procurada globalmente."
        ),
    ),

    CatalogJersey(
        lote=14, clube="Liverpool FC", liga="Premier League", pais="Inglaterra",
        marca="New Balance", tipo="home", periodo="2017-18", patrocinador="Standard Chartered",
        conservacao="Excelente", tag="RARO", vl_min=450, vl_max=710,
        contexto=(
            "Manga longa — versão rara da camisa home do Liverpool. Temporada da final "
            "da Champions League (perdida para o Real Madrid). Salah, Firmino, Mané. "
            "Manga longa eleva raridade e valor."
        ),
    ),

    CatalogJersey(
        lote=15, clube="AC Milan", liga="Serie A", pais="Itália",
        marca="Adidas", tipo="home", periodo="2006-07", patrocinador="Bwin",
        conservacao="Excelente", tag="RARO", vl_min=490, vl_max=750,
        contexto=(
            "Camisa da temporada do 7º título da Champions League do Milan. "
            "Kaká, Seedorf, Inzaghi. Bwin como patrocinador. "
            "Alta liquidez entre colecionadores do futebol italiano."
        ),
    ),

    CatalogJersey(
        lote=16, clube="Real Madrid", liga="La Liga", pais="Espanha",
        marca="Adidas", tipo="third", periodo="2014-15", patrocinador="Emirates",
        conservacao="Excelente", tag="", vl_min=380, vl_max=580,
        contexto=(
            "Third rosa/roxo do Real Madrid — uma das camisas mais comentadas da história do clube. "
            "CR7, Bale, Benzema. Décima Champions (La Décima) vencida na temporada anterior."
        ),
    ),

    CatalogJersey(
        lote=17, clube="Juventus FC", liga="Serie A", pais="Itália",
        marca="Adidas", tipo="away", periodo="2012-13", patrocinador="Jeep",
        conservacao="Excelente", tag="", vl_min=320, vl_max=480,
        contexto=(
            "Away rosa da Juventus — temporada do scudetto com Del Piero em seu último ano. "
            "Jeep como patrocinador (primeiro ano). Pirlo, Vidal, Marchisio."
        ),
    ),

    CatalogJersey(
        lote=18, clube="Atlético de Madrid", liga="La Liga", pais="Espanha",
        marca="Nike", tipo="home", periodo="2013-14", patrocinador="Azerbaijan",
        conservacao="Excelente", tag="JOIA", vl_min=550, vl_max=850,
        contexto=(
            "Camisa do título de La Liga e finalista da Champions 2013-14. "
            "Diego Costa, Courtois, Koke, Griezmann. Simeone revolucionou o clube. "
            "Uma das maiores surpresas da história do futebol europeu."
        ),
    ),

    CatalogJersey(
        lote=19, clube="Seleção Argentina", liga="Internacional", pais="Argentina",
        marca="Adidas", tipo="home", periodo="2014", patrocinador="",
        conservacao="Excelente", tag="JOIA", vl_min=620, vl_max=980,
        contexto=(
            "Camisa da Copa do Mundo Brasil 2014 — Argentina foi vice-campeã (perdeu para "
            "a Alemanha na final). Messi foi eleito melhor jogador. "
            "Altíssima demanda entre colecionadores argentinos e globais."
        ),
    ),

    CatalogJersey(
        lote=20, clube="Seleção Alemanha", liga="Internacional", pais="Alemanha",
        marca="Adidas", tipo="home", periodo="2014", patrocinador="",
        conservacao="Excelente", tag="JOIA", vl_min=650, vl_max=1000,
        contexto=(
            "Camisa da Copa do Mundo Brasil 2014 — Alemanha campeã com 7x1 histórico "
            "contra o Brasil nas semifinais. Müller, Klose, Kroos, Özil. "
            "Uma das camisas mais simbólicas da história do futebol."
        ),
    ),

    # ── Lote 21-30 ────────────────────────────────────────────────────────────

    CatalogJersey(
        lote=21, clube="Chelsea FC", liga="Premier League", pais="Inglaterra",
        marca="Adidas", tipo="third", periodo="2011-12", patrocinador="Samsung",
        conservacao="Excelente", tag="RARO", vl_min=400, vl_max=620,
        contexto=(
            "Third azul marinho da temporada em que o Chelsea venceu a Champions League "
            "(Drogba selou com gol e pênalti). Lampard, Terry, Drogba. "
            "Adidas como fornecedora — parceria rara nesta era."
        ),
    ),

    CatalogJersey(
        lote=22, clube="Ajax", liga="Eredivisie", pais="Holanda",
        marca="Umbro", tipo="home", periodo="1994-95", patrocinador="ABN AMRO",
        conservacao="Boa", tag="JOIA", vl_min=750, vl_max=1200,
        contexto=(
            "Camisa do Ajax campeão da Champions League 1994-95. "
            "Patrick Kluivert, Clarence Seedorf, Frank Rijkaard, Marc Overmars. "
            "Item vintage de altíssima raridade — ABN AMRO histórico."
        ),
    ),

    CatalogJersey(
        lote=23, clube="Seleção Holanda", liga="Internacional", pais="Holanda",
        marca="Nike", tipo="home", periodo="2010", patrocinador="",
        conservacao="Excelente", tag="", vl_min=320, vl_max=500,
        contexto=(
            "Camisa da Copa do Mundo 2010 — Holanda vice-campeã (perdeu para a Espanha). "
            "Robben, Van Persie, Sneijder, Van der Vaart."
        ),
    ),

    CatalogJersey(
        lote=24, clube="Seleção Portugal", liga="Internacional", pais="Portugal",
        marca="Nike", tipo="home", periodo="2016", patrocinador="",
        conservacao="Excelente", tag="RARO", vl_min=420, vl_max=660,
        contexto=(
            "Camisa da Eurocopa 2016 — Portugal campeão (CR7 saiu lesionado na final). "
            "Eder marcou o gol decisivo na prorrogação vs França. "
            "Alta liquidez entre fãs de CR7 e Portugal."
        ),
    ),

    CatalogJersey(
        lote=25, clube="Seleção França", liga="Internacional", pais="França",
        marca="Nike", tipo="home", periodo="2018", patrocinador="",
        conservacao="Excelente", tag="JOIA", vl_min=500, vl_max=800,
        contexto=(
            "Camisa da Copa do Mundo Rússia 2018 — França campeã. "
            "Mbappé, Griezmann, Pogba, Kanté. Mbappé se tornou o 2º jogador "
            "a marcar em final de Copa (após Pelé). Item de alta valorização."
        ),
    ),

    CatalogJersey(
        lote=26, clube="Napoli SSC", liga="Serie A", pais="Itália",
        marca="Reebok", tipo="home", periodo="2000-01", patrocinador="Banca di Roma",
        conservacao="Boa", tag="RARO", vl_min=380, vl_max=580,
        contexto=(
            "Camisa vintage do Napoli era pós-Maradona com Reebok. "
            "Raridade no mercado brasileiro — pouco conhecido fora do circuito italiano. "
            "Alta demanda entre colecionadores de futebol italiano vintage."
        ),
    ),

    CatalogJersey(
        lote=27, clube="Borussia Dortmund", liga="Bundesliga", pais="Alemanha",
        marca="Nike", tipo="home", periodo="2012-13", patrocinador="Evonik",
        conservacao="Excelente", tag="", vl_min=300, vl_max=450,
        contexto=(
            "Camisa do BVB finalista da Champions 2012-13 (perdeu para o Bayern). "
            "Lewandowski, Reus, Götze. Última temporada de Götze antes de ir ao Bayern."
        ),
    ),

    CatalogJersey(
        lote=28, clube="FC Barcelona", liga="La Liga", pais="Espanha",
        marca="Nike", tipo="home", periodo="2014-15", patrocinador="Qatar Airways",
        conservacao="Excelente", tag="JOIA", vl_min=580, vl_max=900,
        contexto=(
            "Camisa do triplete de Luís Enrique — La Liga, Copa del Rey e Champions League. "
            "Messi, Neymar, Suárez formaram o MSN. Considerado um dos melhores ataques da história."
        ),
    ),

    CatalogJersey(
        lote=29, clube="Valencia CF", liga="La Liga", pais="Espanha",
        marca="Umbro", tipo="home", periodo="2003-04", patrocinador="Amstel",
        conservacao="Boa (desgaste leve)", tag="RARO", vl_min=350, vl_max=540,
        contexto=(
            "Valencia campeão de La Liga 2003-04 com Claudio Ranieri. "
            "Umbro como fornecedora — raridade visual. Vicente, Mista, Baraja."
        ),
    ),

    CatalogJersey(
        lote=30, clube="Seleção Italiana", liga="Internacional", pais="Itália",
        marca="Puma", tipo="home", periodo="2006", patrocinador="",
        conservacao="Excelente", tag="JOIA", vl_min=650, vl_max=1000,
        contexto=(
            "Camisa da Copa do Mundo Alemanha 2006 — Itália campeã (Zidane expulso na final). "
            "Cannavaro, Buffon, Totti, Pirlo. Uma das maiores geraçoes da Azzurra. "
            "Altíssima demanda entre colecionadores italianos."
        ),
    ),

    # ── Lote 31-40 ────────────────────────────────────────────────────────────

    CatalogJersey(
        lote=31, clube="Manchester City", liga="Premier League", pais="Inglaterra",
        marca="Umbro", tipo="home", periodo="2011-12", patrocinador="Etihad",
        conservacao="Excelente", tag="", vl_min=300, vl_max=460,
        contexto=(
            "Camisa do primeiro título da Premier League do Manchester City na era moderna. "
            "Agüero marcou o gol no último minuto vs QPR. Início da era Abu Dhabi."
        ),
    ),

    CatalogJersey(
        lote=32, clube="Arsenal FC", liga="Premier League", pais="Inglaterra",
        marca="Nike", tipo="away", periodo="2013-14", patrocinador="Emirates",
        conservacao="Excelente", tag="RARO", vl_min=350, vl_max=530,
        contexto=(
            "Away amarela do Arsenal — design inspirado nas camisas históricas dos anos 70. "
            "Ozil chegou ao clube nesta temporada por £42.5M. Alexis Sánchez, Cazorla, Giroud."
        ),
    ),

    CatalogJersey(
        lote=33, clube="Flamengo", liga="Brasileirão", pais="Brasil",
        marca="Adidas", tipo="home", periodo="2019", patrocinador="Banco do Brasil",
        conservacao="Excelente", tag="JOIA", vl_min=500, vl_max=800,
        contexto=(
            "Camisa do tri-campeão (Brasileiro + Libertadores 2019). "
            "Gabigol, Bruno Henrique, Arrascaeta, Filipe Luís. "
            "Temporada histórica do Flamengo — Libertadores depois de 38 anos."
        ),
    ),

    CatalogJersey(
        lote=34, clube="Santos FC", liga="Brasileirão", pais="Brasil",
        marca="Umbro", tipo="home", periodo="2011", patrocinador="Caixa",
        conservacao="Excelente", tag="JOIA", vl_min=600, vl_max=950,
        contexto=(
            "Camisa do Santos bicampeão da Libertadores 2011. Neymar Jr. na temporada "
            "antes de ir ao Barcelona. Ganso, Elano, Borges. "
            "Alta demanda entre colecionadores de Neymar e do Santos histórico."
        ),
    ),

    CatalogJersey(
        lote=35, clube="Corinthians", liga="Brasileirão", pais="Brasil",
        marca="Nike", tipo="home", periodo="2012", patrocinador="Caixa",
        conservacao="Excelente", tag="RARO", vl_min=400, vl_max=620,
        contexto=(
            "Camisa do Corinthians campeão mundial 2012 (venceu o Chelsea). "
            "Roque Santa Cruz, Danilo, Paolo Guerrero. Clube mais popular do Brasil "
            "conquistando o mundo — alta liquidez no mercado nacional."
        ),
    ),

    CatalogJersey(
        lote=36, clube="Palmeiras", liga="Brasileirão", pais="Brasil",
        marca="Puma", tipo="home", periodo="2021", patrocinador="Crefisa",
        conservacao="Excelente", tag="", vl_min=280, vl_max=420,
        contexto=(
            "Camisa da Copa Libertadores 2021 (bicampeão). Deyverson marcou o gol decisivo. "
            "Abel Ferreira como técnico. Raphael Veiga, Dudu, Zé Rafael."
        ),
    ),

    CatalogJersey(
        lote=37, clube="Olympique de Marseille", liga="Ligue 1", pais="França",
        marca="Adidas", tipo="home", periodo="1992-93", patrocinador="Panasonic",
        conservacao="Boa", tag="JOIA", vl_min=700, vl_max=1100,
        contexto=(
            "Camisa do único título de Champions League do Marseille (1992-93). "
            "Didier Deschamps, Rudi Völler, Alen Bokšić. Escândalo de suborno posterior. "
            "Item vintage extremamente raro — praticamente impossível de encontrar."
        ),
    ),

    CatalogJersey(
        lote=38, clube="Celtic FC", liga="Scottish Premiership", pais="Escócia",
        marca="New Balance", tipo="home", periodo="2016-17", patrocinador="Dafabet",
        conservacao="Excelente", tag="RARO", vl_min=300, vl_max=460,
        contexto=(
            "Celtic invicto no campeonato escocês 2016-17 (Treble). "
            "Brendan Rodgers como técnico. Scott Brown, Moussa Dembélé. "
            "Raridade no mercado brasileiro."
        ),
    ),

    CatalogJersey(
        lote=39, clube="SSC Napoli", liga="Serie A", pais="Itália",
        marca="Ea7", tipo="third", periodo="2022-23", patrocinador="Ebay",
        conservacao="Excelente", tag="RARO", vl_min=450, vl_max=700,
        contexto=(
            "Third do Napoli campeão da Serie A 2022-23 depois de 33 anos. "
            "Osimhen, Kvara, Di Lorenzo, Lobotka. Design inusitado com Ea7 Emporio Armani. "
            "Muito procurada globalmente após o título histórico."
        ),
    ),

    CatalogJersey(
        lote=40, clube="Seleção Espanha", liga="Internacional", pais="Espanha",
        marca="Adidas", tipo="home", periodo="2010", patrocinador="",
        conservacao="Excelente", tag="JOIA", vl_min=600, vl_max=950,
        contexto=(
            "Camisa da Copa do Mundo África do Sul 2010 — Espanha campeã pela primeira vez. "
            "Iniesta marcou o gol decisivo na final. Casillas, Xavi, Villa, Piqué, Ramos. "
            "Geração mais vitoriosa da história do futebol espanhol."
        ),
    ),

    # ── Lote 41-49 ────────────────────────────────────────────────────────────

    CatalogJersey(
        lote=41, clube="Galatasaray SK", liga="Süper Lig", pais="Turquia",
        marca="Adidas", tipo="home", periodo="1999-00", patrocinador="Opel",
        conservacao="Boa", tag="RARO", vl_min=400, vl_max=620,
        contexto=(
            "Galatasaray campeão da Copa UEFA e Supercopa da UEFA em 1999-2000. "
            "Hakan Şükür, Hasan Şaş, Popescu, Jardel. Único clube turco a vencer a UEFA."
        ),
    ),

    CatalogJersey(
        lote=42, clube="Bayer Leverkusen", liga="Bundesliga", pais="Alemanha",
        marca="Adidas", tipo="home", periodo="2023-24", patrocinador="Bayer",
        conservacao="Excelente", tag="JOIA", vl_min=550, vl_max=850,
        contexto=(
            "Leverkusen campeão invicto da Bundesliga 2023-24 com Xabi Alonso. "
            "Granit Xhaka, Florian Wirtz, Victor Boniface. "
            "Quebraram hegemonia do Bayern de 11 anos — camisa histórica."
        ),
    ),

    CatalogJersey(
        lote=43, clube="Club Atlético River Plate", liga="Primera División", pais="Argentina",
        marca="Adidas", tipo="home", periodo="2018", patrocinador="Zurich",
        conservacao="Excelente", tag="RARO", vl_min=380, vl_max=580,
        contexto=(
            "River Plate campeão da Libertadores 2018 — final jogada em Madri (vs Boca). "
            "Martínez Quarta, Pratto, Nacho Fernández. Alta demanda no mercado argentino."
        ),
    ),

    CatalogJersey(
        lote=44, clube="Grêmio FBPA", liga="Brasileirão", pais="Brasil",
        marca="Umbro", tipo="home", periodo="2017", patrocinador="Banrisul",
        conservacao="Excelente", tag="RARO", vl_min=350, vl_max=540,
        contexto=(
            "Grêmio campeão da Copa Libertadores 2017. Luan, Everton, Fernandinho. "
            "Renato Gaúcho como técnico. Alta liquidez no mercado gaúcho e regional."
        ),
    ),

    CatalogJersey(
        lote=45, clube="São Paulo FC", liga="Brasileirão", pais="Brasil",
        marca="Reebok", tipo="home", periodo="2005", patrocinador="Claro",
        conservacao="Boa", tag="RARO", vl_min=420, vl_max=650,
        contexto=(
            "Camisa do São Paulo tricampeão do mundo 2005. "
            "Rogério Ceni, Mineiro, Cicinho, Danilo Pereira. "
            "Reebok como fornecedora — raridade visual para colecionadores do SPFC."
        ),
    ),

    CatalogJersey(
        lote=46, clube="Internacional FC", liga="Brasileirão", pais="Brasil",
        marca="Penalty", tipo="home", periodo="2006", patrocinador="Banrisul",
        conservacao="Excelente", tag="RARO", vl_min=380, vl_max=580,
        contexto=(
            "Inter campeão da Copa Libertadores 2006 e do Mundial 2006. "
            "Adriano Gabiru, Fernandão, Tinga. Penalty como fornecedora histórica."
        ),
    ),

    CatalogJersey(
        lote=47, clube="Seleção Uruguai", liga="Internacional", pais="Uruguai",
        marca="Puma", tipo="home", periodo="2010", patrocinador="",
        conservacao="Excelente", tag="RARO", vl_min=320, vl_max=500,
        contexto=(
            "Uruguai 4º colocado na Copa 2010 — Suárez foi expulso pela mão na linha e "
            "Ghanés chutou o pênalti pra fora. Diego Forlán ganhou Bola de Ouro do torneio. "
            "Raridade no mercado brasileiro."
        ),
    ),

    CatalogJersey(
        lote=48, clube="Seleção Colombiana", liga="Internacional", pais="Colômbia",
        marca="Adidas", tipo="home", periodo="2014", patrocinador="",
        conservacao="Excelente", tag="RARO", vl_min=350, vl_max=540,
        contexto=(
            "Colômbia na Copa 2014 — James Rodríguez foi o artilheiro com 6 gols "
            "e ganhou o Prêmio Puskás. Cuadrado, Ospina, Falcao (fora por lesão). "
            "Alta demanda entre fãs de James Rodríguez."
        ),
    ),

    CatalogJersey(
        lote=49, clube="Seleção Brasileira", liga="Internacional", pais="Brasil",
        marca="Nike", tipo="home", periodo="2002", patrocinador="",
        conservacao="Excelente", tag="JOIA", vl_min=800, vl_max=1350,
        contexto=(
            "Camisa da Copa do Mundo Coreia/Japão 2002 — Brasil pentacampeão. "
            "Ronaldo Fenômeno ressurge após convulsão e marca 2 gols na final vs Alemanha. "
            "Ronaldinho, Rivaldo, Roberto Carlos, Cafu. "
            "Uma das camisas mais valiosas do futebol brasileiro de todos os tempos."
        ),
    ),
]


# ── ÍNDICES PARA LOOKUP RÁPIDO ─────────────────────────────────────────────────

# Lookup por clube (normalized)
_CLUB_INDEX: dict[str, list[CatalogJersey]] = {}
for jersey in CATALOG:
    key = jersey.clube.lower()
    _CLUB_INDEX.setdefault(key, []).append(jersey)

# Lookup por país
_COUNTRY_INDEX: dict[str, list[CatalogJersey]] = {}
for jersey in CATALOG:
    key = jersey.pais.lower()
    _COUNTRY_INDEX.setdefault(key, []).append(jersey)

# Joias e assinadas — alta prioridade de compra
JOIAS = [j for j in CATALOG if j.is_joia]
ASSINADAS = [j for j in CATALOG if j.is_assinada]
RARAS = [j for j in CATALOG if j.is_raro]


_STOPWORDS = {"de", "do", "da", "as", "os", "fc", "ac", "sc", "sk", "if", "cf", "of", "the"}


def _club_matches(club_name: str, title_lower: str) -> bool:
    """True se o clube for identificável no título com baixo risco de falso positivo."""
    padded = f" {title_lower} "
    words = [w for w in club_name.lower().split() if w not in _STOPWORDS]

    # Siglas curtas (PSG, BVB, etc.) — exige espaço em volta (word boundary simulado)
    abbrevs = [w for w in words if len(w) <= 3]
    long_words = [w for w in words if len(w) >= 4]

    # Qualquer palavra longa presente → match
    if any(w in title_lower for w in long_words):
        return True
    # Sigla curta → exige aparição com espaços em torno
    if any(f" {w} " in padded for w in abbrevs):
        return True
    return False


def find_catalog_match(title: str) -> Optional[CatalogJersey]:
    """
    Verifica se um anúncio corresponde a alguma camisa do catálogo pessoal.
    Útil para: estimar preço de revenda, verificar se é concorrente ou oportunidade.
    """
    title_lower = title.lower()
    best: Optional[CatalogJersey] = None
    best_score = 0

    for jersey in CATALOG:
        score = 0
        # Club match (mais importante)
        if _club_matches(jersey.clube, title_lower):
            score += 3
        # Period match — year must appear
        if jersey.periodo[:4] in title_lower:
            score += 2
        # Brand match
        if jersey.marca.lower() in title_lower:
            score += 1
        # Type match (away, home, third)
        if jersey.tipo.lower() in title_lower:
            score += 1

        if score > best_score and score >= 3:
            best_score = score
            best = jersey

    return best


def get_catalog_price_reference(title: str) -> Optional[tuple[float, float]]:
    """
    Retorna (vl_min, vl_max) do catálogo se encontrar match, None caso contrário.
    Usado pelo price_tracker como quarto tier de estimativa.
    """
    match = find_catalog_match(title)
    if match:
        return (match.vl_min, match.vl_max)
    return None


def get_catalog_stats() -> dict:
    """Resumo do catálogo para debug/logging."""
    return {
        "total": len(CATALOG),
        "joias": len(JOIAS),
        "assinadas": len(ASSINADAS),
        "raras": len(RARAS),
        "valor_total_min": sum(j.vl_min for j in CATALOG),
        "valor_total_max": sum(j.vl_max for j in CATALOG),
        "valor_medio_por_peca": sum(j.vl_medio for j in CATALOG) / len(CATALOG),
        "paises": list({j.pais for j in CATALOG}),
    }


# Termos de times/eras que enriquecem o SPORTS_CONTEXT do red_flags
CATALOG_SPORTS_CONTEXT: list[str] = list({
    term.lower()
    for jersey in CATALOG
    for term in [
        *jersey.clube.lower().split(),
        jersey.pais.lower(),
        jersey.liga.lower().split()[0],  # primeira palavra da liga
    ]
    if len(term) > 3
})
