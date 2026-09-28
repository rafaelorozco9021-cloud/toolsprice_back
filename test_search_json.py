import httpx, asyncio, json, re
async def t():
    headers={'User-Agent':'Mozilla/5.0','Accept-Language':'es-CO,es;q=0.9','Referer':'https://www.homecenter.com.co/'}
    async with httpx.AsyncClient(timeout=20, follow_redirects=True, headers=headers) as c:
        for url in [
            "https://www.homecenter.com.co/homecenter-co/search/?Ntt=tubo%20pvc",
            "https://www.homecenter.com.co/homecenter-co/search/?text=tubo%20pvc",
            "https://www.homecenter.com.co/api/search?query=tubo%20pvc",
        ]:
            r=await c.get(url, headers={**headers, "Accept":"application/json"})
            print(url, r.status_code, r.headers.get('content-type','')[:50], len(r.text))
            print(r.text[:1500])
            print("---")
import asyncio
asyncio.run(t())
