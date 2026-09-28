import httpx, asyncio, re
async def t():
    headers={'User-Agent':'Mozilla/5.0'}
    async with httpx.AsyncClient(timeout=20, follow_redirects=True, headers=headers) as c:
        r=await c.get("https://www.homecenter.com.co/sodimac-catalyst-bu-prod-browse-sitemaps/soco-browse-category-sitemap.xml")
        print(r.status_code, len(r.text))
        txt=r.text
        # find urls containing pintura
        for m in re.findall(r'<loc>([^<]*pintura[^<]*)</loc>', txt, re.I)[:20]:
            print(m)
        print("--- soldadura ---")
        for m in re.findall(r'<loc>([^<]*soldadura[^<]*)</loc>', txt, re.I)[:20]:
            print(m)
        print("--- plomeria ---")
        for m in re.findall(r'<loc>([^<]*plomer[^<]*)</loc>', txt, re.I)[:20]:
            print(m)
        print("--- construccion ---")
        for m in re.findall(r'<loc>([^<]*construccion[^<]*)</loc>', txt, re.I)[:20]:
            print(m)

import asyncio
asyncio.run(t())
