import httpx
import asyncio
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

async def test():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    async with httpx.AsyncClient(timeout=10, headers=headers, verify=False, follow_redirects=True) as client:
        url = "https://www.momoshop.com.tw/TP/TP0006390/goodsDetail/TP00063900000201"
        r = await client.get(url)
        print("TP goods URL Status:", r.status_code)
        print("Is sold out / error message in text:", "熱銷一空" in r.text)
        print("Page title:", r.text[r.text.find("<title>"):r.text.find("</title>")+8] if "<title>" in r.text else "None")

if __name__ == "__main__":
    asyncio.run(test())
