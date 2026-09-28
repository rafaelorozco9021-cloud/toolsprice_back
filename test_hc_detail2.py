import httpx, asyncio, json, re
from bs4 import BeautifulSoup

async def test():
    url="https://www.homecenter.com.co/homecenter-co/product/354581/cemento-gris-topex-uso-general-50kg/354581/"
    headers={'User-Agent':'Mozilla/5.0','Accept-Language':'es-CO,es;q=0.9'}
    async with httpx.AsyncClient(timeout=20, follow_redirects=True, headers=headers) as c:
        r=await c.get(url)
        soup=BeautifulSoup(r.text,'html.parser')
        nxt=soup.find('script', id='__NEXT_DATA__')
        data=json.loads(nxt.string)
        j=json.dumps(data, ensure_ascii=False, indent=2)
        # find price
        # search for "price"
        import re
        m=re.findall(r'"price[^"]*"\s*:\s*"?(\d+)"?', j)
        print(m[:20])
        # dump productProps
        pp=data['props']['pageProps'].get('productProps',{})
        print(json.dumps(list(pp.keys())))
        res=pp.get('result',{})
        print(json.dumps(list(res.keys()) if isinstance(res, dict) else str(res)[:500])[:2000])
        # variants
        if 'variants' in res:
            print(json.dumps(res['variants'][:1], indent=2, ensure_ascii=False)[:3000])
        # also check offers in ld+json product priceCurrency
        # already did

asyncio.run(test())
