import httpx
import asyncio
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

async def test():
    # 測試多種 Shopee 請求管道
    urls = [
        "https://shopee.tw/api/v4/search/search_items?by=relevancy&keyword=%E6%98%A5%E9%A2%A8%E5%B9%B3%E6%9D%BF%E8%11%9B%E7%94%9F%E7%B4%99&limit=10&newest=0&order=desc&page_type=search&scenario=PAGE_GLOBAL_SEARCH&version=2",
        "https://mall.shopee.tw/api/v4/search/search_items?by=relevancy&keyword=%E6%98%A5%E9%A2%A8%E5%B9%B3%E6%9D%BF%E8%11%9B%E7%94%9F%E7%B4%99&limit=10",
        "https://feeds.shopee.tw/universal-link/search?keyword=%E6%98%A5%E9%A2%A8%E5%B9%B3%E6%9D%BF%E8%11%9B%E7%94%9F%E7%B4%99"
    ]
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "X-Shopee-Language": "zh-Hant",
        "Referer": "https://shopee.tw/"
    }

    async with httpx.AsyncClient(timeout=5, headers=headers, follow_redirects=True) as client:
        for u in urls:
            try:
                r = await client.get(u)
                print(f"URL: {u[:60]} -> Status: {r.status_code}, Length: {len(r.text)}")
            except Exception as e:
                print(f"Error {u[:60]}: {e}")

if __name__ == "__main__":
    asyncio.run(test())
