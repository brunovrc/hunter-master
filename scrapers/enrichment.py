"""
Enriquecimento de anúncios Enjoei/OLX — busca descrição completa e galeria de
fotos na página de detalhe do anúncio, algo que os cards de busca não expõem.

Por quê: o pipeline de IA estava recebendo description="" e só 1 foto (a
thumbnail do card de busca) para esses dois scrapers. Isso fazia a IA nunca
ver menções a COA/certificado no texto do vendedor, nem fotos adicionais do
certificado/etiqueta — levando a falsos "suspeita de falsidade".

Só roda para listings que já passaram pelo filtro de sinal de colecionador
(bot_core._has_collector_signal) — mantém o custo de navegação extra restrito
aos candidatos que já valeriam o custo de IA de qualquer forma.

IMPORTANTE: cada item usa um CONTEXT novo (não só uma nova aba). Testado ao
vivo: reaproveitar a mesma aba pra navegar de anúncio em anúncio dispara o
desafio do Cloudflare ("Attention Required") já no 2º acesso — mesmo com
delay entre as navegações. Contexto novo por item (identidade/cookies novos,
mesmo processo de browser) evita o bloqueio sem multiplicar o custo de abrir
um browser inteiro a cada item.
"""
import logging
import re

from playwright.async_api import async_playwright

from .anti_detection import get_browser_context, human_delay

logger = logging.getLogger(__name__)

_MAX_IMAGES = 5

# Título de página quando o Cloudflare (ou proteção similar) bloqueia o acesso
_BLOCK_SIGNALS = ["attention required", "just a moment", "cloudflare", "access denied"]


async def _is_blocked(page) -> bool:
    title = (await page.title() or "").lower()
    return any(s in title for s in _BLOCK_SIGNALS)


async def _enrich_enjoei(page, url: str) -> tuple[str, list[str]]:
    await page.goto(url, wait_until="domcontentloaded", timeout=30000)
    await human_delay(2.0, 4.0)
    if await _is_blocked(page):
        raise RuntimeError("bloqueado por proteção anti-bot")

    description = ""
    el = await page.query_selector(".l-product-details__description-text")
    if el:
        description = (await el.inner_text() or "").strip()

    images = []
    slug_match = re.search(r"/p/([a-z0-9-]+)", url)
    slug = slug_match.group(1) if slug_match else ""
    if slug:
        imgs = await page.query_selector_all(f'img[src*="{slug}/100x100/"]')
        seen_hashes = set()
        for img in imgs:
            src = await img.get_attribute("src") or ""
            hash_part = src.rsplit("/", 1)[-1]
            if hash_part and hash_part not in seen_hashes:
                seen_hashes.add(hash_part)
                # 800xN = resolução alta o suficiente pra IA ler etiqueta/COA
                images.append(src.replace("/100x100/", "/800xN/"))
            if len(images) >= _MAX_IMAGES:
                break

    return description, images


async def _enrich_olx(page, url: str) -> tuple[str, list[str]]:
    await page.goto(url, wait_until="domcontentloaded", timeout=30000)
    await human_delay(2.0, 4.0)
    if await _is_blocked(page):
        raise RuntimeError("bloqueado por proteção anti-bot")

    description = ""
    spans = await page.query_selector_all("span.typo-body-medium")
    texts = []
    for s in spans:
        t = (await s.inner_text() or "").strip()
        if t:
            texts.append(t)
    if texts:
        # A descrição é sempre o texto mais longo entre os spans desse tipo
        # (os outros são preço, categoria, localização — todos curtos)
        description = max(texts, key=len)

    images = []
    imgs = await page.query_selector_all('img[src*="img.olx.com.br"]')
    seen = set()
    for img in imgs:
        src = await img.get_attribute("src") or ""
        if src and src not in seen:
            seen.add(src)
            images.append(src)
        if len(images) >= _MAX_IMAGES:
            break

    return description, images


_ENRICHERS = {
    "enjoei": _enrich_enjoei,
    "olx": _enrich_olx,
}


async def enrich_listings(listings: list[dict]) -> list[dict]:
    """
    Enriquece em lote os listings de plataformas suportadas (Enjoei/OLX).
    Cada item recebe um browser+context novo (identidade/cookies frescos) —
    necessário para evitar o bloqueio do Cloudflare que aparece ao
    reaproveitar a mesma sessão entre navegações consecutivas (testado ao
    vivo: 2ª navegação com a mesma aba já cai em "Attention Required").
    Falhas individuais não derrubam o lote: o listing original é mantido
    como fallback se a página de detalhe falhar ou for bloqueada.
    """
    candidates = [l for l in listings if l.get("platform") in _ENRICHERS and l.get("url")]
    if not candidates:
        return listings

    async with async_playwright() as p:
        for listing in candidates:
            enricher = _ENRICHERS[listing["platform"]]
            browser = None
            try:
                browser, context = await get_browser_context(p, locale="pt-BR")
                page = await context.new_page()
                description, images = await enricher(page, listing["url"])
                if description:
                    listing["description"] = description
                if images:
                    listing["images"] = images
                logger.debug(
                    f"[Enrich] {listing['platform']} '{listing.get('title','')[:40]}' — "
                    f"desc={len(description)} chars, {len(images)} imagens"
                )
            except Exception as e:
                logger.warning(
                    f"[Enrich] {listing['platform']} falhou pra "
                    f"{listing.get('url','')[:60]}: {e}"
                )
            finally:
                if browser:
                    await browser.close()

    return listings
