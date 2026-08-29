import re
from typing import List, Set
from app.models.product import ProductItem, ComparisonGroup

class ProductMatcher:
    """智慧商品標題正規化與跨平台同款比價聚合器"""

    NOISE_PATTERNS = [
        r"【.*?】",
        r"\[.*?\]",
        r"\(.*?\)",
        r"（.*?）",
        r"★.*?★",
        r"◆.*?◆",
        r"▼.*?▼",
        r"📣|❤️|🔥|⭐|✨|⚡|💥|👉|✔️|🏆|💎",
        r"\b(現貨|公司貨|原廠|官方|旗艦|熱銷|熱賣|特惠|下殺|狂降|免運|正品|保固|24h|速達|含發票|開發票|附發票|店到店|超商|秒出|兩年保固|一年保固|原廠盒裝|台灣公司貨|全新|二手|9成新|95成新|福利品|出清|展示品)\b",
        r"送.*?元",
        r"限時.*?",
        r"滿.*?(折|送|折抵)",
    ]

    @classmethod
    def clean_title(cls, title: str) -> str:
        cleaned = title
        for pattern in cls.NOISE_PATTERNS:
            cleaned = re.sub(pattern, " ", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"[^\w\s\.\-\+]", " ", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned

    @classmethod
    def group_similar_products(cls, items: List[ProductItem], keyword: str = "") -> List[ComparisonGroup]:
        """將同一搜尋目標的所有電商與賣家報價聚合在同一個比價大卡片中，避免切碎為孤立單件區塊"""
        valid_items = [it for it in items if it.price > 0]
        if not valid_items:
            return []

        # 依價格由低到高嚴格排序
        sorted_items = sorted(valid_items, key=lambda x: x.price)
        lowest_item = sorted_items[0]
        highest_item = sorted_items[-1]
        
        diff = highest_item.price - lowest_item.price
        diff_percent = round((diff / highest_item.price) * 100, 1) if highest_item.price > 0 else 0.0
        platforms = list(dict.fromkeys([it.platform for it in sorted_items]))

        # 生成代表性標題
        group_title = f"「{keyword.strip()}」跨平台比價與各賣家報價清單" if keyword.strip() else (cls.clean_title(lowest_item.title) or lowest_item.title)

        main_group = ComparisonGroup(
            group_id="grp_master_main",
            normalized_title=group_title,
            lowest_price=lowest_item.price,
            highest_price=highest_item.price,
            price_diff=diff,
            price_diff_percent=diff_percent,
            best_deal_item=lowest_item,
            items=sorted_items,
            platforms_available=platforms
        )

        return [main_group]
