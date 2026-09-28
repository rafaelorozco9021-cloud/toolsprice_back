from playwright.async_api import async_playwright
import asyncio, json

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox'])
        ctx = await browser.new_context(user_agent='Mozilla/5.0')
        page = await ctx.new_page()
        reqs=[]
        def on_req(req):
            url=req.url
            if 'search' in url.lower() or 'api' in url.lower() or 'algolia' in url.lower() or 'sodimac' in url.lower():
                reqs.append((req.method, url, req.headers.get('authorization','')[:50]))
                print(f"REQ: {req.method} {url}")
        page.on("request", on_req)
        page.on("response", lambda r: print(f"RES: {r.status} {r.url[:120]}") if 'search' in r.url.lower() else None)
        print("Goto homecenter search...")
        await page.goto("https://www.homecenter.com.co/homecenter-co/search/?text=cemento", wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(8000)
        # also try typing in search bar
        try:
            # wait for products
            await page.wait_for_selector("[data-testid*='product']", timeout=5000)
            print("found product selector")
        except:
            print("no product selector, content len", len(await page.content()))
            print((await page.content())[:3000])
        print("Captured reqs:", reqs[:20])
        # dump html
        html=await page.content()
        with open("/tmp/hc_play.html","w",encoding="utf-8") as f:
            f.write(html)
        print("saved html", len(html))
        await browser.close()

asyncio.run(main())
