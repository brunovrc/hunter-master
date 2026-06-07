"""
Roda isso para ver o HTML real da Enjoei e descobrir os seletores corretos.
  python debug_enjoei.py
"""
import asyncio

from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        )
        page = await context.new_page()

        url = "https://www.enjoei.com.br/s?q=camisa+autografada"
        print(f"Abrindo: {url}")
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(6)

        title = await page.title()
        print(f"Título da página: {title}")

        # Tenta diferentes seletores e mostra quantos encontrou
        selectors = [
            "[data-testid='product-card']",
            "article",
            "li[class*='product']",
            "div[class*='ProductCard']",
            "a[href*='/p/']",
            "[class*='card']",
            "[class*='Card']",
            "[class*='item']",
            "[class*='Item']",
        ]

        for sel in selectors:
            els = await page.query_selector_all(sel)
            print(f"  {sel!r:50s} → {len(els)} elementos")

        # Salva HTML dos primeiros 8000 chars pra inspecionar
        html = await page.content()
        with open("enjoei_debug.html", "w", encoding="utf-8") as f:
            f.write(html)
        print(f"\nHTML salvo em enjoei_debug.html ({len(html)} chars)")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
