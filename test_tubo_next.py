import httpx, asyncio, json
from bs4 import BeautifulSoup
async def t():
    headers={'User-Agent':'Mozilla/5.0','Accept-Language':'es-CO,es;q=0.9'}
    async with httpx.AsyncClient(timeout=20, follow_redirects=True, headers=headers) as c:
        r=await c.get("https://www.homecenter.com.co/homecenter-co/search/?Ntt=tubo%20pvc")
        soup=BeautifulSoup(r.text,'html.parser')
        nxt=soup.find('script', id='__NEXT_DATA__')
        if nxt:
            data=json.loads(nxt.string)
            jstr=json.dumps(data)
            print("len", len(jstr))
            # find product names in jstr
            import re
            m=re.findall(r'"name"\s*:\s*"([^"]*Tubo[^"]*)"', jstr)
            print(m[:5])
            # check searchProps
            print(json.dumps(data['props']['pageProps'].get('searchProps',{}), indent=2)[:2000])
            # also check for products in props
            s=json.dumps(data)
            idx=s.find("Tubo")
            print(s[idx-500:idx+2000][:3000] if idx!=-1 else "no Tubo")
import asyncio
asyncio.run(t())
