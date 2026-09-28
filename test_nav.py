import httpx, asyncio, json, re
async def t():
    headers={'User-Agent':'Mozilla/5.0','Accept-Language':'es-CO,es;q=0.9'}
    async with httpx.AsyncClient(timeout=20, follow_redirects=True, headers=headers) as c:
        r=await c.get("https://www.homecenter.com.co/homecenter-co/category/cat10002/pinturas-y-accesorios/")
        print("pintura cat status", r.status_code, len(r.text))
        from bs4 import BeautifulSoup
        soup=BeautifulSoup(r.text,'html.parser')
        ld=[s.string for s in soup.find_all('script', type='application/ld+json') if s.string and 'Product' in s.string]
        print("pintura ld products", len(ld))
        if ld:
            import json
            try:
                data=json.loads(ld[0])
                print(ld[0][:2000])
            except: print(ld[0][:1000])

        # also test soldadura category guesses
        for url in [
            "https://www.homecenter.com.co/homecenter-co/category/cat10038/soldadura/",
            "https://www.homecenter.com.co/homecenter-co/category/cat373002/soldadura/",
            "https://www.homecenter.com.co/homecenter-co/category/cat10796/Plomeria/",
            "https://www.homecenter.com.co/homecenter-co/category/cat10007/plomeria/",
            "https://www.homecenter.com.co/homecenter-co/category/cat206001/pinturas/",
        ]:
            try:
                rr=await c.get(url)
                print(url, rr.status_code, len(rr.text))
                soup2=BeautifulSoup(rr.text,'html.parser')
                has=len([s for s in soup2.find_all('script', type='application/ld+json') if s.string and 'Product' in s.string])
                print(" -> products", has)
            except Exception as e: print(e)

import asyncio
asyncio.run(t())
