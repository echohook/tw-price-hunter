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
            
            shopee_only = []
            for it in items:
                store = it.get("data-store") or ""
                title = it.get("data-title") or ""
                price = it.get("data-price") or "0"
                dest_url = it.get("data-url") or ""
                print(f" - Found Store: [{store}] | Title: {title[:30]} | Price: {price}")
                if "蝦皮" in store:
                    shopee_only.append((store, title, price, dest_url))

            print(f"\nStrict Shopee verified items count: {len(shopee_only)}")
            for s, t, p, u in shopee_only[:3]:
                print(f"   -> [{s}] NT$ {p} | {t[:40]}")

if __name__ == "__main__":
    asyncio.run(test())
