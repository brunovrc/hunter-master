"""
Utilitários de anti-detecção para scrapers Playwright.
Uso: importar get_browser_context() no lugar de criar context manualmente.
"""

import asyncio
import random

USER_AGENTS = [
    # Chrome Windows — mais comum
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    # Chrome Mac
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    # Firefox
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.4; rv:124.0) Gecko/20100101 Firefox/124.0",
    # Edge
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0",
]

VIEWPORTS = [
    {"width": 1280, "height": 800},
    {"width": 1366, "height": 768},
    {"width": 1440, "height": 900},
    {"width": 1920, "height": 1080},
    {"width": 1536, "height": 864},
]

INIT_SCRIPTS = [
    # Remove webdriver flag
    "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})",
    # Simula plugins reais
    """
    Object.defineProperty(navigator, 'plugins', {
        get: () => [
            {name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer'},
            {name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai'},
            {name: 'Native Client', filename: 'internal-nacl-plugin'}
        ]
    });
    """,
    # Lingua
    "Object.defineProperty(navigator, 'languages', {get: () => ['pt-BR', 'pt', 'en-US', 'en']})",
]


def random_user_agent() -> str:
    return random.choice(USER_AGENTS)


def random_viewport() -> dict:
    return random.choice(VIEWPORTS)


async def human_delay(min_s: float = 1.5, max_s: float = 4.5):
    """Delay aleatório simulando comportamento humano."""
    await asyncio.sleep(random.uniform(min_s, max_s))


async def get_browser_context(playwright, locale: str = "pt-BR"):
    """
    Cria browser + context com perfil anti-detecção completo.
    Retorna (browser, context) — fechar ambos no finally.
    """
    browser = await playwright.chromium.launch(
        headless=True,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--disable-infobars",
            "--window-size=1280,800",
            "--disable-extensions",
        ],
    )

    ua = random_user_agent()
    vp = random_viewport()

    accept_lang = "pt-BR,pt;q=0.9,en;q=0.8" if locale == "pt-BR" else "es-AR,es;q=0.9,en;q=0.8"

    context = await browser.new_context(
        user_agent=ua,
        locale=locale,
        viewport=vp,
        extra_http_headers={
            "Accept-Language": accept_lang,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
        },
        java_script_enabled=True,
        bypass_csp=False,
    )

    for script in INIT_SCRIPTS:
        await context.add_init_script(script)

    return browser, context


# ── Seletores resilientes com múltiplos fallbacks ─────────────────────────────

async def safe_text(element, selectors: list[str]) -> str:
    """Tenta cada seletor em ordem, retorna texto do primeiro que funcionar."""
    for sel in selectors:
        try:
            el = await element.query_selector(sel)
            if el:
                text = (await el.inner_text()).strip()
                if text:
                    return text
        except Exception:
            continue
    return ""


async def safe_attr(element, selectors: list[str], attr: str) -> str:
    """Tenta cada seletor em ordem, retorna atributo do primeiro que funcionar."""
    for sel in selectors:
        try:
            el = await element.query_selector(sel)
            if el:
                val = await el.get_attribute(attr)
                if val:
                    return val.strip()
        except Exception:
            continue
    return ""


async def wait_for_any(page, selectors: list[str], timeout: int = 15000) -> bool:
    """Aguarda qualquer dos seletores aparecer na página."""
    import asyncio
    tasks = [
        asyncio.create_task(_wait_sel(page, sel, timeout))
        for sel in selectors
    ]
    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
    for t in pending:
        t.cancel()
    return any(not t.exception() and t.result() for t in done)


async def _wait_sel(page, selector: str, timeout: int) -> bool:
    try:
        await page.wait_for_selector(selector, timeout=timeout)
        return True
    except Exception:
        return False
