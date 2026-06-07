import asyncio
from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            locale="pt-BR",
            viewport={"width": 1280, "height": 800},
            extra_http_headers={
                "Accept-Language": "pt-BR,pt;q=0.9",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            },
        )
        page = await context.new_page()

        url = "https://www.mercadolivre.com.br/jm/search?as_word=camisa+autografada+futebol"
        print(f"Abrindo: {url}")
        await page.goto(url, wait_until="networkidle", timeout=60000)
        await asyncio.sleep(4)

        title = await page.title()
        print(f"Título: {title}")

        selectors = [
            "li.ui-search-layout__item",
            ".ui-search-result__wrapper",
            ".ui-search-result",
            ".ui-search-layout__item",
            "[class*='ui-search']",
            ".andes-card",
            "ol.ui-search-layout > li",
            "section.ui-search-results > ol > li",
        ]

        for sel in selectors:
            els = await page.query_selector_all(sel)
            print(f"  {sel!r:55s} → {len(els)} elementos")

        # Pega o HTML interno do primeiro card para ver a estrutura real
        first = await page.query_selector("li.ui-search-layout__item")
        if first:
            inner = await first.inner_html()
            print("\n--- HTML do primeiro card ---")
            print(inner[:3000])
        else:
            print("\nNenhum card encontrado!")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
