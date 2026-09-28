import httpx, asyncio
async def main():
    async with httpx.AsyncClient(timeout=10, follow_redirects=True) as c:
        r=await c.get("https://www.homecenter.com.co/robots.txt", headers={"User-Agent":"Mozilla/5.0"})
        print(r.status_code)
        print(r.text[:4000])
asyncio.run(main())
