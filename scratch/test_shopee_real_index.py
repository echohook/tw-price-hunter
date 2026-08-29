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
    
    async with httpx.AsyncClient(timeout=10, headers=headers, follow_redirects=True) as client:
        for kw in ["春風平板衛生紙", "羅技 M720", "iPhone 16"]:
            url = f"https://feebee.com.tw/s/{urllib.parse.quote(kw)}/?mode=s&shop=shopee"
            r = await client.get(url)
            print(f"\n=================== Keyword: {kw} ===================")
            soup = bs4.BeautifulSoup(r.text, "html.parser")
            items = soup.select("li.items")
            print(f"Items found: {len(items)}")
            for it in items[:6]:
                title = it.get("data-title")
                price = it.get("data-price")
                store = it.get("data-store")
                url_dest = it.get("data-url")
                img_elem = it.select_one("img")
                img_src = img_elem.get("src") or img_elem.get("data-src") if img_elem else ""
                print(f" - [{store}] NT$ {price} | {title} | URL: {url_dest[:40]} | Img: {img_src[:50]}")

if __name__ == "__main__":
    asyncio.run(test())
