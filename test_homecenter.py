import httpx, asyncio, json, re
from bs4 import BeautifulSoup

async def test():
    headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36','Accept-Language':'es-CO,es;q=0.9'}
    url='https://www.homecenter.com.co/homecenter-co/search/?text=cemento'
    async with httpx.AsyncClient(follow_redirects=True, timeout=30, headers=headers) as c:
        r = await c.get(url)
        txt=r.text
        print("STATUS", r.status_code, "len", len(txt))
        # find NEXT_DATA
        soup=BeautifulSoup(txt,'html.parser')
        nxt=soup.find('script', id='__NEXT_DATA__')
        if nxt:
            data=json.loads(nxt.string)
            # dump to file
            with open('/tmp/next.json','w',encoding='utf-8') as f:
                json.dump(data,f,ensure_ascii=False,indent=2)
            print("NEXT_DATA dumped, keys", list(data.keys()))
            # search for api endpoint in all scripts
            for s in soup.find_all('script'):
                t=s.string or ''
                if 'algolia' in t.lower() or 'search' in t.lower() and 'api' in t.lower():
                    print(t[:1000])
                    break
        # find all script src
        for s in soup.find_all('script', src=True):
            print("src:", s['src'][:120])
        # regex for api
        m=re.findall(r"https://[^\s\"']+search[^\s\"']*", txt)
        uniq=list(set(m))[:20]
        print("search urls found:", uniq)

asyncio.run(test())
