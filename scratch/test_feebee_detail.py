import httpx
import asyncio
import sys
import bs4
import urllib.parse

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

async def test():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }
    url = f"https://feebee.com.tw/s/{urllib.parse.quote('羅技 M720')}/"
    async with httpx.AsyncClient(timeout=10, headers=headers, follow_redirects=True) as client:
        r = await client.get(url)
        soup = bs4.BeautifulSoup(r.text, "html.parser")
        items = soup.select("li.items")
        if items:
            it = items[0]
            print("Item HTML snippet:")
            print(it.prettify()[:1000])

if __name__ == "__main__":
    asyncio.run(test())
