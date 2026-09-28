from app.scrapers.homecenter import HomecenterScraper
import asyncio, json

async def t():
    import httpx
    from bs4 import BeautifulSoup
    url="https://www.homecenter.com.co/homecenter-co/category/cat10038/soldadura/"
    s=HomecenterScraper()
    html=await s._fetch(url)
    prods=s._parse_ldjson_search(html)
    print(len(prods))
    for p in prods[:10]:
        print(p["nombre"], "|", p["precio"], "|", p["url_producto"][:60])

asyncio.run(t())
