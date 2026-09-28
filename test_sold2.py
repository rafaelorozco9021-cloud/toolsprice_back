import asyncio
from app.scrapers.homecenter import HomecenterScraper
async def t():
    s=HomecenterScraper()
    for url in [
        "https://www.homecenter.com.co/homecenter-co/category/cat1670263/adhesivos-soldaduras-y-teflones/",
        "https://www.homecenter.com.co/homecenter-co/category/cat1670261/pastas-y-soldaduras-de-estano-y-plata/",
        "https://www.homecenter.com.co/homecenter-co/category/cat80102/herramientas-de-plomeria-y-soldadura/",
        "https://www.homecenter.com.co/homecenter-co/category/cat40446116/pinturas-para-metal-interior/",
        "https://www.homecenter.com.co/homecenter-co/category/cat10462/pinturas/",
        "https://www.homecenter.com.co/homecenter-co/category/cat10796/plomeria/",
    ]:
        html=await s._fetch(url)
        prods=s._parse_ldjson_search(html)
        print(url, len(prods), prods[0]["nombre"][:50] if prods else "0")

import asyncio
asyncio.run(t())
