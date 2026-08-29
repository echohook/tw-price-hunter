import httpx
import asyncio
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

async def test():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"}
    async with httpx.AsyncClient(timeout=10, headers=headers, follow_redirects=True) as client:
        r = await client.get("https://rtapi.ruten.com.tw/api/search/v3/index.php/core/prod?q=羅技+M720&type=direct&sort=rnk%2Fdc&offset=1&limit=10")
        data = r.json()
        rows = data.get("Rows", [])
        id_list = [row.get("Id") for row in rows if row.get("Id")]
        ids_str = ",".join(id_list)
        r_detail = await client.get(f"https://rtapi.ruten.com.tw/api/prod/v2/index.php/prod?id={ids_str}")
        d_data = r_detail.json()
        print(f"Ruten products returned: {len(d_data)}")
        for item in d_data[:5]:
            print(f"Name: {item.get('ProdName')}")
            print(f" - Price: {item.get('PriceRange')}")
            print(f" - Img: {item.get('Image')}")
            print(f" - ID: {item.get('ProdId')}")
            print(f" - StockStatus: {item.get('StockStatus')}")

if __name__ == "__main__":
    asyncio.run(test())
