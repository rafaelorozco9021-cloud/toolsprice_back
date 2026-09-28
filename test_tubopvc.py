from app.scrapers.homecenter import HomecenterScraper
import asyncio
async def t():
    s=HomecenterScraper()
    for q in ["tubo pvc","tubo","pvc"]:
        r=await s.search(q)
        print(q, len(r))
        for p in r[:5]:
            print(" ", p["nombre"][:60], "|", p["precio"], "|", p["categoria"])
        print("---")
    # also test search_all
    r2=await s.search_all_categories("tubo pvc")
    print("search_all tubo pvc", len(r2))
    for p in r2[:5]:
        print(" ", p["nombre"][:60])

import asyncio
asyncio.run(t())
