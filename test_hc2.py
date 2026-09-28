import httpx, asyncio, re

async def fetch_js():
    headers={'User-Agent':'Mozilla/5.0'}
    async with httpx.AsyncClient(timeout=20, follow_redirects=True, headers=headers) as c:
        # fetch search chunk
        url="https://static.falabella.io/sodimac-b2c-ui/prod-so/cd12079d/_next/static/chunks/pages/search-af591ce791dc4db623a6.js"
        r=await c.get(url)
        txt=r.text
        print(len(txt))
        # find fetch/axios/api
        for pat in [r"api[^\"']*search", r"algolia", r"homecenter[^\"']*search", r"/search", r"falabella.*api"]:
            m=re.findall(pat, txt, re.I)
            if m:
                print(pat, m[:10])
        # also search for sodimac search api domain
        m=re.findall(r"https://[^\s\"']+", txt)
        uniq=[x for x in m if "api" in x.lower() or "search" in x.lower()][:30]
        print(uniq)
        # check for browse
        if "sodimac" in txt.lower():
            idx=txt.lower().find("sodimac")
            print(txt[idx-500:idx+2000][:3000])

asyncio.run(fetch_js())
