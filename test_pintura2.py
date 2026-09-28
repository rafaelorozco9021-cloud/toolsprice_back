import httpx, asyncio
from bs4 import BeautifulSoup
import json
async def t():
    headers={'User-Agent':'Mozilla/5.0','Accept-Language':'es-CO,es;q=0.9'}
    async with httpx.AsyncClient(timeout=20, follow_redirects=True, headers=headers) as c:
        for url in [
            "https://www.homecenter.com.co/homecenter-co/category/cat10462/pinturas/",
            "https://www.homecenter.com.co/homecenter-co/category/cat1680181/pintura-para-interior/",
            "https://www.homecenter.com.co/homecenter-co/category/cat9050089/pinturas-y-accesorios-mundo-eco-produccion-sustentable/",
        ]:
            r=await c.get(url)
            soup=BeautifulSoup(r.text,'html.parser')
            cnt=len([s for s in soup.find_all('script', type='application/ld+json') if s.string and 'Product' in s.string])
            print(url, cnt, len(r.text))
            if cnt:
                for s in soup.find_all('script', type='application/ld+json'):
                    if s.string and 'Product' in s.string:
                        data=json.loads(s.string)
                        if isinstance(data, dict) and data.get('@type')=='WebPage':
                            offers=data.get('mainEntity',{}).get('offers',{}).get('itemOffered',[])
                            print("  products", len(offers) if isinstance(offers, list) else 1)
                            if isinstance(offers, list) and offers:
                                print("   first", offers[0].get('name')[:50])
                        break

import asyncio
asyncio.run(t())
