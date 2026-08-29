import sys, os, asyncio
sys.path.insert(0, os.path.abspath('backend'))
sys.path.insert(0, os.path.abspath('.'))
if sys.platform == 'win32':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass

from scratch.test_strict_category import strict_product_filter
from app.services.aggregator import aggregator

async def test_all():
    queries = [
        "makita 40v 無線砂紙機",
        "makita 無線打蠟機",
        "羅技 M720",
        "春風平板衛生紙",
        "PS5 Slim",
        "iPhone 16"
    ]
    for q in queries:
        res = await aggregator.search(q, use_cache=False)
        passed = [it for it in res.results if strict_product_filter(it.title, q)]
        print(f"\n=== Query: {q} (Raw: {res.total_found} -> Passed: {len(passed)}) ===")
        for it in passed[:3]:
            print(f"  - [{it.platform}] NT$ {it.price} | {it.title[:45]}")

asyncio.run(test_all())
