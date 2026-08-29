import sys, os, asyncio
sys.path.insert(0, os.path.abspath('backend'))
if sys.platform == 'win32':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass

from app.services.aggregator import aggregator

async def test():
    # 測試春風平板衛生紙在各平台的真實搜尋結果
    res = await aggregator.search('春風平板衛生紙', use_cache=False)
    print(f'Total items found: {res.total_found}')
    for it in res.results[:10]:
        print(f'[{it.platform}] NT$ {it.price} | {it.title[:30]} | URL: {it.product_url} | Img: {it.image_url[:50]}')

asyncio.run(test())
