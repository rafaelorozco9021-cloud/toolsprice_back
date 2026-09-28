import httpx, asyncio
from bs4 import BeautifulSoup
import json

async def check(url):
    headers={'User-Agent':'Mozilla/5.0','Accept-Language':'es-CO,es;q=0.9'}
    async with httpx.AsyncClient(timeout=20, follow_redirects=True, headers=headers) as c:
        r=await c.get(url)
        soup=BeautifulSoup(r.text,'html.parser')
        prods=[s.string for s in soup.find_all('script', type='application/ld+json') if s.string and 'Product' in s.string]
        cnt=0
        first=""
        if prods:
            try:
                data=json.loads(prods[0])
                if data.get('@type')=='WebPage':
                    offers=data.get('mainEntity',{}).get('offers',{}).get('itemOffered',[])
                    cnt=len(offers) if isinstance(offers, list) else 1
                    if isinstance(offers, list) and offers:
                        first=offers[0].get('name','')[:60]
                else:
                    cnt=1
            except: pass
        print(url, "->", r.status_code, "products", cnt, "first", first[:50])

async def t():
    for u in [
        "https://www.homecenter.com.co/homecenter-co/category/cat30038/herramientas-manuales/",
        "https://www.homecenter.com.co/homecenter-co/category/cat301008/kit-de-herramientas-manuales/",
        "https://www.homecenter.com.co/homecenter-co/category/cat720001/construccion-y-ferreteria/",
        "https://www.homecenter.com.co/homecenter-co/category/cat10190009/instalacion-de-construccion/",
        "https://www.homecenter.com.co/sodimac-catalyst-bu-prod-browse-sitemaps/soco-browse-category-sitemap.xml",
    ]:
        if "sitemap" in u:
            import re
            headers={'User-Agent':'Mozilla/5.0'}
            async with httpx.AsyncClient(timeout=20, follow_redirects=True, headers=headers) as c:
                r=await c.get(u)
                for m in re.findall(r'<loc>([^<]*herramienta[^<]*)</loc>', r.text, re.I)[:8]:
                    print(m)
                for m in re.findall(r'<loc>([^<]*brocha[^<]*)</loc>', r.text, re.I)[:8]:
                    print(m)
        else:
            await check(u)

import asyncio
asyncio.run(t())
