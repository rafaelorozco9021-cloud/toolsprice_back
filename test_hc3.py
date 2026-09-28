import httpx, asyncio, json, re
from bs4 import BeautifulSoup

async def test():
    headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36','Accept-Language':'es-CO,es;q=0.9','Referer':'https://www.homecenter.com.co/'}
    async with httpx.AsyncClient(timeout=20, follow_redirects=True, headers=headers) as c:
        # probar categoria materiales
        urls = [
            "https://www.homecenter.com.co/homecenter-co/category/cat290003/materiales-de-construccion/",
            "https://www.homecenter.com.co/homecenter-co/search/?Ntt=cemento",
            "https://www.homecenter.com.co/homecenter-co/search?Ntt=cemento",
        ]
        for url in urls:
            try:
                r=await c.get(url)
                print(url, r.status_code, len(r.text))
                if r.status_code==200:
                    soup=BeautifulSoup(r.text,'html.parser')
                    # print title
                    print(" title", soup.title.get_text()[:100] if soup.title else "")
                    # find json ld
                    lds=soup.find_all('script', type='application/ld+json')
                    print(" ld+json", len(lds))
                    for ld in lds[:1]:
                        print(ld.string[:2000] if ld.string else "empty")
                    # find __NEXT_DATA__
                    nxt=soup.find('script', id='__NEXT_DATA__')
                    if nxt:
                        data=json.loads(nxt.string)
                        # buscar dentro todo el json dumps product/cemento
                        jstr=json.dumps(data)
                        if 'cemento' in jstr.lower():
                            idx=jstr.lower().find('cemento')
                            print(jstr[idx-500:idx+2000][:3000])
                        else:
                            print("no cemento in NEXT_DATA")
                    print("---")
            except Exception as e:
                print("err",e)

asyncio.run(test())
