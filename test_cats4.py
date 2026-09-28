from app.scrapers.homecenter import HomecenterScraper
import asyncio

async def t():
    s=HomecenterScraper()
    for q in ['cemento','soldadura','pintura','plomeria']:
        r=await s.search(q, categoria=q)
        print(q, len(r), r[0]['nombre'][:55] if r else '0', r[0]['precio'] if r else '', r[0]['tienda'] if r else '')

asyncio.run(t())
