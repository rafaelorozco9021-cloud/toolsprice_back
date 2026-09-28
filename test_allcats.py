import asyncio
from app.scrapers.homecenter import HomecenterScraper

async def t():
    s=HomecenterScraper()
    for q in ['soldadura','pintura','plomeria','cemento','arena','varilla']:
        r=await s.search(q)
        print(q, len(r), [x["nombre"][:50] for x in r[:2]])

import asyncio
asyncio.run(t())
