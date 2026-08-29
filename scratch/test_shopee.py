import httpx
import asyncio
import sys
import bs4

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

async def test():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-TW,zh;q=0.9",
    }

    async with httpx.AsyncClient(timeout=10, headers=headers, follow_redirects=True) as client:
        r = await client.get("https://shopee.tw/search?keyword=%E7%BE%85%E6%8A%80%20m720")
        print("Length:", len(r.text))
        for target in ["923", "925", "943", "960", "Triathlon", "M720"]:
            pos = r.text.find(target)
            print(f"Target '{target}' in HTML: {pos}")
            if pos != -1:
                print("Snippet:", r.text[pos-100:pos+200])

if __name__ == "__main__":
    asyncio.run(test())
