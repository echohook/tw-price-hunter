import sys, os, asyncio
sys.path.insert(0, os.path.abspath('backend'))
if sys.platform == 'win32':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass

import re
from typing import List, Set
from app.models.product import ProductItem, ComparisonGroup

class SmartMatcher:
    @classmethod
    def clean_title(cls, title: str) -> str:
        # 移除促銷雜詞
        noise = [r"【.*?】", r"\[.*?\]", r"\(.*?\)", r"（.*?）", r"★.*?★", r"◆.*?◆", r"▼.*?▼",
                 r"📣|❤️|🔥|⭐|✨|⚡|💥|👉|✔️|🏆", r"\b(現貨|公司貨|原廠|官方|旗艦|熱銷|熱賣|特惠|下殺|狂降|免運|正品|保固|24h|速達|含發票|開發票|附發票|店到店|超商|秒出)\b"]
        c = title
        for n in noise:
            c = re.sub(n, " ", c, flags=re.IGNORECASE)
        c = re.sub(r"[^\w\s\.\-\+]", " ", c)
        return re.sub(r"\s+", " ", c).strip()

    @classmethod
    def group_similar_products(cls, items: List[ProductItem], keyword: str = "") -> List[ComparisonGroup]:
        valid_items = [it for it in items if it.price > 0]
        if not valid_items:
            return []

        # 1. 統一歸納為核心主比價群組 (避免切碎為 40 個只有 1 件商品的空區塊)
        # 所有符合搜尋目標的商品，集中在同一個大卡片中，依價格由低到高排序
        sorted_items = sorted(valid_items, key=lambda x: x.price)
        lowest_item = sorted_items[0]
        highest_item = sorted_items[-1]
        diff = highest_item.price - lowest_item.price
        diff_percent = round((diff / highest_item.price) * 100, 1) if highest_item.price > 0 else 0.0
        platforms = list(set([it.platform for it in valid_items]))
        
        main_title = f"「{keyword}」全網比價與報價清單" if keyword else (cls.clean_title(lowest_item.title) or lowest_item.title)

        main_group = ComparisonGroup(
            group_id="grp_master_main",
            normalized_title=main_title,
            lowest_price=lowest_item.price,
            highest_price=highest_item.price,
            price_diff=diff,
            price_diff_percent=diff_percent,
            best_deal_item=lowest_item,
            items=sorted_items,
            platforms_available=platforms
        )

        return [main_group]

from app.services.aggregator import aggregator

async def test():
    # 測試 RTX 4070 搜尋與聚合
    res = await aggregator.search("RTX 4070", platforms=["ruten"], use_cache=False)
    print("Total items:", res.total_found)
    groups = SmartMatcher.group_similar_products(res.results, keyword="RTX 4070")
    print("Groups count:", len(groups))
    for g in groups:
        print(f"Group: {g.normalized_title} -> 共有 {len(g.items)} 件商品 (最低 NT$ {g.lowest_price} ~ 最高 NT$ {g.highest_price})，跨 {len(g.platforms_available)} 平台")

asyncio.run(test())
