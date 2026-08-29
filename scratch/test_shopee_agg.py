import httpx
import asyncio
import sys
import bs4
import re
import urllib.parse

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

async def test():
    # 測試透過公開電商索引抓取蝦皮商品 (例如 DuckDuckGo / Bing / Google Shopping / Feebee / BigGo 等)
    kw = "春風平板衛生紙"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }
    
    async with httpx.AsyncClient(timeout=10, headers=headers, follow_redirects=True) as client:
        # Method 1: DuckDuckGo HTML search for site:shopee.tw
        try:
            ddg_url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(kw)}+site%3Ashopee.tw"
            r = await client.get(ddg_url)
            print("DDG search status:", r.status_code, "Length:", len(r.text))
            soup = bs4.BeautifulSoup(r.text, "html.parser")
            results = soup.find_all("div", class_="result")
            print("DDG results count:", len(results))
            for res in results[:5]:
                title_elem = res.find("a", class_="result__snippet") or res.find("a", class_="result__url")
                t_elem = res.find("a", class_="result__title")
                snippet_elem = res.find("a", class_="result__snippet")
                print(" - Title:", t_elem.text.strip() if t_elem else "None")
                print("   Snippet:", snippet_elem.text.strip() if snippet_elem else "None")
        except Exception as e:
            print("DDG error:", e)

        # Method 2: Feebee (飛比價格) 蝦皮專區 / Open search
        try:
            feebee_url = f"https://feebee.com.tw/s/{urllib.parse.quote(kw)}/?mode=s&shop=shopee"
            r_fb = await client.get(feebee_url)
            print("\nFeebee Shopee status:", r_fb.status_code, "Length:", len(r_fb.text))
            if r_fb.status_code == 200:
                soup_fb = bs4.BeautifulSoup(r_fb.text, "html.parser")
                items = soup_fb.find_all("li", class_="pure-u-1-2") or soup_fb.find_all("li", class_="item") or soup_fb.find_all("div", class_="pure-g")
                print("Feebee items found:", len(items))
                # Check for product titles and prices
                for it in soup_fb.select("li.items")[:5]:
                    print("Feebee item:", it.get_text()[:100])
        except Exception as e:
            print("Feebee error:", e)

if __name__ == "__main__":
    asyncio.run(test())
