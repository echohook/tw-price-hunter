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
        for kw in ["羅技 M720", "春風平板衛生紙"]:
            url = f"https://feebee.com.tw/s/{urllib.parse.quote(kw)}/"
            r = await client.get(url)
            print(f"\n=== Feebee Search: {kw} (Status: {r.status_code}) ===")
            soup = bs4.BeautifulSoup(r.text, "html.parser")
            items = soup.select("li.items")
            print(f"Total items found: {len(items)}")
            for it in items[:5]:
                title = it.select_one(".title") or it.select_one("h3") or it.select_one("a.item_title")
                price = it.select_one(".price")
                img = it.select_one("img")
                link = it.select_one("a")
                shop = it.select_one(".shop")
                t_txt = title.get_text(strip=True) if title else "No title"
                p_txt = price.get_text(strip=True) if price else "No price"
                s_txt = shop.get_text(strip=True) if shop else "General"
                img_src = img.get("src") or img.get("data-src") if img else "No img"
                print(f" - [{s_txt}] NT$ {p_txt} | {t_txt[:35]} | Img: {img_src[:45]}")

if __name__ == "__main__":
    asyncio.run(test())
