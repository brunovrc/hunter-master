# Hunter Master — Spec v1.0

Sistema automatizado de hunting de memorabilia esportiva para Camisas Clássicas.

---

## O que é

Agente de software que varre continuamente marketplaces e plataformas de memorabilia em busca de oportunidades de aquisição de camisetas autografadas, match-worn e retrô vintage. Para cada anúncio, aplica dois estágios de análise e envia notificações em tempo real via Telegram e email quando detecta oportunidade com margem mínima de 40%.

---

## Arquitetura

```
CAMADA 1 — HUNTER         →  CAMADA 2 — HUNTER MASTER  →  NOTIFICAÇÕES
Scrapers + Filtro local      7 Filtros comerciais           Telegram + Email
+ Claude API                 + Recomendação final           (tempo real)
```

**Números-chave:**
- Varredura a cada 30 minutos
- Latência de notificação < 5 minutos
- Margem mínima para COMPRAR: 40%
- Custo estimado MVP: R$ 50–100/mês

---

## Fontes de dados

### Tier 1 — Marketplaces brasileiros (Sprint 1)
| Plataforma | Método | Observação |
|---|---|---|
| Mercado Livre | API oficial OAuth2 | Alto volume, dados estruturados |
| OLX | Playwright headless | Vendedores PF, oportunidades brutas |
| Enjoei | BeautifulSoup4 | Nicho de colecionáveis |
| Shopee | Playwright | Sprint 2 |

### Tier 2 — Memorabilia especializada (Sprint 2)
| Plataforma | Método | Observação |
|---|---|---|
| MatchWornShirt | Playwright | Autenticação Fabricks NFC |
| eBay | API oficial | Volume global, referência internacional |
| Hall da Fama BR | BeautifulSoup4 | COA com perito grafotécnico |
| Memorabília BR | BeautifulSoup4 | SB Brasil — 1ª certificadora BR |
| Catawiki | Playwright | Sprint 3 — leilões europeus |

### Tier 3 — Referência de preço / concorrentes (diário)
SR Futebol, Brechó do Futebol, FutClassics, Atrox, Play for a Cause

### Tier 4 — Social e internacional (Sprint 3–4)
Facebook Marketplace, Instagram hashtags, Heritage Auctions

---

## Os 7 Filtros Hunter Master

| # | Filtro | Pts | O que avalia |
|---|---|---|---|
| F1 | Margem Bruta | 30 | ((Venda - Compra) / Venda) × 100 ≥ 40% |
| F2 | Autenticidade | 25 | COA verificável (PSA/DNA, Beckett, JSA, SB Brasil, Fabricks) + Claude Vision |
| F3 | Turnover | 15 | Match-worn ídolo: 30–60d. Retrô raro: 90–180d. Regional: >180d |
| F4 | Reputacional | 10 | Atleta em polêmica? Clube em crise? Flag para análise |
| F5 | Mix de Estoque | 5 | Risco de canibalização? Diversificação vs concentração sul-americana |
| F6 | Vendedor | 10 | Histórico na plataforma. Conta nova + item raro = red flag |
| F7 | Demanda Futura | 10 | Copa 2026 (+15pts), Libertadores (+8pts), aniversários de conquistas |

**Matriz de decisão:**
- COMPRAR AGORA: todos verdes + margem ≥ 40% + score ≥ 60
- NEGOCIAR: filtros ok, margem 20–40% — sugere oferta exata
- FLAG AUTENTICADOR: autenticidade não verificável visualmente
- RECUSAR: red flag crítico, margem < 20% ou turnover ruim

---

## Red Flags

| Nível | Código | Ação |
|---|---|---|
| CRÍTICO | EXPLICIT_FAKE | Descarte automático |
| CRÍTICO | AUTOPEN_SUSPECTED | Descarte automático |
| CRÍTICO | MASS_LISTING | Descarte automático |
| CRÍTICO | LIKELY_FAKE_VISUAL | Descarte automático |
| ALTO | NEW_SELLER_HIGH_VALUE | Score zerado F6 |
| ALTO | NO_IMAGES | Score zerado F2 |
| ALTO | INCONSISTENT_LABEL | Flag autenticador |
| ALTO | TEXT_FAKE_SUSPECTED | Penalidade -15pts |
| MÉDIO | SINGLE_IMAGE | Penalidade -5pts |
| MÉDIO | VISUAL_FLAG | Penalidade -5pts |

---

## Stack técnica

**Coleta:** Playwright, httpx + asyncio, BeautifulSoup4, Scrapy (Sprint 3+)
**IA:** Claude API Sonnet 4 (texto), Claude Vision (autenticidade visual)
**Banco:** SQLAlchemy ORM / SQLite (dev) → PostgreSQL (produção) / Redis (Sprint 3+)
**Notificações:** python-telegram-bot, SendGrid
**Infra:** APScheduler, Circuit Breaker, Railway ou VPS Hetzner, Docker (Sprint 2+)

---

## Estrutura de arquivos (Sprint 1)

```
hunter-master/
  main.py                      # Orquestrador, scheduler, health check
  config/
    settings.py                # Configurações via pydantic-settings + .env
    players.py                 # Banco de jogadores, valores de referência, eventos futuros
  scrapers/
    base.py                    # Circuit breaker, deduplicação, filtro local, rate limiting
    mercadolivre.py            # API oficial OAuth2
    olx.py                     # Playwright headless
    enjoei.py                  # BeautifulSoup4
    tier3_pricer.py            # Varre concorrentes Tier 3
  analysis/
    claude_analyzer.py         # Claude API: texto + Vision
    red_flags.py               # Detecção determinística de fraudes
    score_engine.py            # 7 filtros + relatório + recomendação
  database/
    models.py                  # Listing, Seller, PriceHistory, Tier3Price, Analysis, RunLog
    db.py                      # Conexão async SQLite/Postgres
    price_tracker.py           # Média dinâmica Tier 3 + fallback
  notifications/
    telegram_bot.py            # Botões inline, relatório diário, health alert
    email_sender.py            # Emails HTML via SendGrid
    formatter.py               # Formatação Telegram e HTML
  tests/
    test_score_engine.py       # 12 testes: 7 filtros, red flags, Hunter Master
  .env.example
  requirements.txt
```

---

## Notificações

**Telegram (tempo real):** disparada quando score ≥ 65 ou flag autenticador. Inclui botões inline: Ver anúncio, Oferecer valor (se NEGOCIAR), Marcar autenticador.

**Email HTML (SendGrid):** relatório completo com tabela por filtro, cálculo de margem, red flags, recomendação e handoff.

**Relatório diário (20h):** anúncios varridos, novos, oportunidades, contagem por recomendação, fontes com erro, tempo médio de análise.

---

## Plano de execução

**Sprint 1 (semanas 1–2) — MVP local:**
ML (API) + OLX + Enjoei + score engine + Claude Vision + SQLite + Telegram + Email + APScheduler + 12 testes pytest

**Sprint 2 (semanas 3–5) — Escala:**
MatchWornShirt + eBay + Hall da Fama BR + Docker + proxy rotativo + watcher de preços + PostgreSQL/Alembic

**Sprint 3 (mês 2) — Inteligência comercial:**
Shopee + Catawiki + FB Marketplace + Redis + banco de estoque real + histórico cross-sessão de vendedores

**Sprint 4 (mês 3+) — Automação avançada:**
Multi-usuário + watchlists + Celery + dashboard web + Heritage Auctions + WhatsApp

---

## Custos estimados MVP

| Serviço | Custo |
|---|---|
| Claude API Sonnet 4 | R$ 25–75/mês |
| Railway | R$ 25/mês |
| SendGrid | Gratuito (100/dia) |
| Telegram Bot | Gratuito |
| ML API + eBay API | Gratuito |
| Proxy (Sprint 2+) | R$ 150–250/mês |
| **Total MVP** | **R$ 50–100/mês** |

---

## Checklist de setup

1. API key Anthropic (console.anthropic.com)
2. Telegram Bot via @BotFather
3. Conta SendGrid + verificar domínio SPF/DKIM
4. App Mercado Livre (developers.mercadolivre.com.br)
5. App eBay Developer (developer.ebay.com)
6. `pip install -r requirements.txt`
7. `playwright install chromium`
8. `cp .env.example .env` e preencher keys
9. `python main.py`
