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
    kw = "春風平板衛生紙"
    url = f"https://feebee.com.tw/s/{urllib.parse.quote(kw)}/?mode=s&shop=shopee"
    
    async with httpx.AsyncClient(timeout=10, headers=headers, follow_redirects=True) as client:
        r = await client.get(url)
        print("Status:", r.status_code)
        soup = bs4.BeautifulSoup(r.text, "html.parser")
        items = soup.select("li.items") or soup.select("div.item") or soup.select(".pure-u-1")
        print("Total selector items:", len(items))
        for it in items[:6]:
            title = it.select_one(".title") or it.select_one("h3") or it.select_one("h2") or it.select_one("a.item_title")
            price = it.select_one(".price") or it.select_one(".price_format")
            img = it.select_one("img")
            link = it.select_one("a")
            shop = it.select_one(".shop") or it.select_one(".source")
            print("---")
            print("Title:", title.get_text(strip=True) if title else "None")
            print("Price:", price.get_text(strip=True) if price else "None")
            print("Img:", img.get("src") or img.get("data-src") if img else "None")
            print("Link:", link.get("href") if link else "None")
            print("Shop:", shop.get_text(strip=True) if shop else "None")

if __name__ == "__main__":
    asyncio.run(test())
