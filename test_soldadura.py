import httpx, asyncio, re, json
from bs4 import BeautifulSoup

async def t():
    headers={'User-Agent':'Mozilla/5.0','Accept-Language':'es-CO,es;q=0.9','Referer':'https://www.homecenter.com.co/'}
    async with httpx.AsyncClient(timeout=20, follow_redirects=True, headers=headers) as c:
        for q in ['soldadura','pintura','plomeria']:
            for url in [f'https://www.homecenter.com.co/homecenter-co/search/?Ntt={q}', f'https://www.homecenter.com.co/homecenter-co/search/?text={q}']:
                r=await c.get(url)
                print(q, url, "->", str(r.url)[:120], r.status_code, len(r.text))
                soup=BeautifulSoup(r.text,'html.parser')
                ld=[s.string[:200] for s in soup.find_all('script', type='application/ld+json') if s.string and 'Product' in s.string][:1]
                print("  ld product?", bool(ld))
                if ld:
                    print("  ld snippet", ld[0][:500])
                # check __NEXT_DATA__ for categoryProps
                nxt=soup.find('script', id='__NEXT_DATA__')
                if nxt:
                    try:
                        data=json.loads(nxt.string)
                        # find urls in jstr
                        jstr=json.dumps(data)
                        # find category urls
                        m=re.findall(r'https://www.homecenter.com.co/homecenter-co/category/[^\"]+', jstr)
                        uniq=list(set(m))[:3]
                        print("  cats in NEXT_DATA", uniq[:3])
                    except: pass
                print()

import asyncio
asyncio.run(t())
