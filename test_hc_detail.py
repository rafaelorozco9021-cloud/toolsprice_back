import httpx, asyncio, json
from bs4 import BeautifulSoup

async def test_detail():
    headers={'User-Agent':'Mozilla/5.0','Accept-Language':'es-CO,es;q=0.9','Referer':'https://www.homecenter.com.co/'}
    url="https://www.homecenter.com.co/homecenter-co/product/354581/cemento-gris-topex-uso-general-50kg/354581/"
    async with httpx.AsyncClient(timeout=20, follow_redirects=True, headers=headers) as c:
        r=await c.get(url)
        print("status", r.status_code, len(r.text))
        soup=BeautifulSoup(r.text,'html.parser')
        # ld+json
        for ld in soup.find_all('script', type='application/ld+json'):
            txt=ld.string or ''
            try:
                data=json.loads(txt)
                print(json.dumps(data, indent=2, ensure_ascii=False)[:5000])
            except:
                # sometimes contains multiple objects?
                print(txt[:3000])
                if '"Product"' in txt:
                    import re
                    # find first Product
                    m=re.search(r'\{.*"@type":"Product".*?\}\s*\]', txt, re.S)
                    if m:
                        print(m.group(0)[:3000])
        # find specs / caracteristicas
        # look for divs with Caracteristicas / Especificaciones
        for h in soup.find_all(string=lambda t: t and "caracter" in t.lower()):
            print("caracter found:", h.strip()[:100], "parent", h.parent.name)
        for div in soup.select('[data-testid]'):
            txt=div.get_text()[:200].replace("\n"," ")
            if "caracter" in txt.lower() or "especific" in txt.lower() or "peso" in txt.lower():
                print(div.get('data-testid'), txt[:200])
        # dump NEXT_DATA if exists
        nxt=soup.find('script', id='__NEXT_DATA__')
        if nxt:
            import json
            data=json.loads(nxt.string)
            jstr=json.dumps(data)
            if "caracter" in jstr.lower():
                idx=jstr.lower().find("caracter")
                print(jstr[idx-500:idx+2000][:3000])
            else:
                print("no caracter in NEXT_DATA, but props pageProps", list(data.get('props',{}).keys())[:10])
                # look for pdp data
                try:
                    import re
                    print(json.dumps(data)[:4000])
                except: pass

asyncio.run(test_detail())
