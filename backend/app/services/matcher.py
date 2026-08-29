import re
from typing import List, Dict
from app.models.product import ProductItem, ComparisonGroup

class ProductMatcher:
    """商品標題正規化與跨平台同款聚合器"""

    # 常見促銷贅詞與符號清理規則
    NOISE_PATTERNS = [
        r"【.*?】",
        r"\[.*?\]",
        r"\(.*?\)",
        r"（.*?）",
        r"★.*?★",
        r"◆.*?◆",
        r"▼.*?▼",
        r"\b(現貨|公司貨|原廠|官方|旗艦|熱銷|熱賣|特惠|下殺|狂降|免運|正品|保固|24h|速達)\b",
        r"送.*?元",
        r"限時.*?",
        r"滿.*?(折|送|折抵)",
    ]

    @classmethod
    def clean_title(cls, title: str) -> str:
        cleaned = title
        for pattern in cls.NOISE_PATTERNS:
            cleaned = re.sub(pattern, " ", cleaned, flags=re.IGNORECASE)
        # 移除多餘空白與特殊字元
        cleaned = re.sub(r"[^\w\s\.\-\+]", " ", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned

    @classmethod
    def calculate_similarity(cls, title1: str, title2: str) -> float:
        """計算兩商品標題的 Jaccard 單詞相似度"""
        c1 = cls.clean_title(title1).lower()
        c2 = cls.clean_title(title2).lower()
        
        words1 = set(c1.split())
        words2 = set(c2.split())
        
        if not words1 or not words2:
            return 0.0
            
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        return len(intersection) / len(union)

    @classmethod
    def group_similar_products(cls, items: List[ProductItem], similarity_threshold: float = 0.45) -> List[ComparisonGroup]:
        """將抓取自不同平台的同款商品自動分組"""
        valid_items = [it for it in items if it.price > 0]
        if not valid_items:
            return []

        clusters: List[List[ProductItem]] = []

        for item in valid_items:
            assigned = False
            for cluster in clusters:
                # 與 cluster 中的第一件商品比較相似度
                sim = cls.calculate_similarity(item.title, cluster[0].title)
                # 且確保是不同平台或相同主型號
                if sim >= similarity_threshold:
                    cluster.append(item)
                    assigned = True
                    break
            if not assigned:
                clusters.append([item])

        # 篩選出跨多平台或有多件報價的群組
        comparison_groups: List[ComparisonGroup] = []
        for idx, group_items in enumerate(clusters):
            # 排序找出最低價
            sorted_items = sorted(group_items, key=lambda x: x.price)
            lowest_item = sorted_items[0]
            highest_item = sorted_items[-1]
            
            lowest_p = lowest_item.price
            highest_p = highest_item.price
            diff = highest_p - lowest_p
            diff_percent = round((diff / highest_p) * 100, 1) if highest_p > 0 else 0.0

            platforms = list(set([it.platform for it in group_items]))
            normalized_title = cls.clean_title(lowest_item.title) or lowest_item.title

            comparison_groups.append(
                ComparisonGroup(
                    group_id=f"grp_{idx}_{lowest_item.id}",
                    normalized_title=normalized_title,
                    lowest_price=lowest_p,
                    highest_price=highest_p,
                    price_diff=diff,
                    price_diff_percent=diff_percent,
                    best_deal_item=lowest_item,
                    items=sorted_items,
                    platforms_available=platforms
                )
            )

        # 依據商品豐富度與價差優先度排序
        comparison_groups.sort(key=lambda g: (len(g.platforms_available), len(g.items), g.price_diff_percent), reverse=True)
        return comparison_groups
