import re
from typing import List, Set
from app.models.product import ProductItem, ComparisonGroup

class ProductMatcher:
    """智慧商品標題正規化與跨平台同款聚合器"""

    NOISE_PATTERNS = [
        r"【.*?】",
        r"\[.*?\]",
        r"\(.*?\)",
        r"（.*?）",
        r"★.*?★",
        r"◆.*?◆",
        r"▼.*?▼",
        r"\b(現貨|公司貨|原廠|官方|旗艦|熱銷|熱賣|特惠|下殺|狂降|免運|正品|保固|24h|速達|含發票|開發票|附發票|店到店|超商|秒出|兩年保固|一年保固|原廠盒裝|台灣公司貨|全新|二手|9成新|95成新|福利品|出清|展示品)\b",
        r"送.*?元",
        r"限時.*?",
        r"滿.*?(折|送|折抵)",
        r"📣|❤️|🔥|⭐|✨|⚡",
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
    def extract_core_tokens(cls, title: str) -> Set[str]:
        """提取商品關鍵字元 (包含英文型號、數字、品牌)"""
        c = cls.clean_title(title).lower()
        # 英文/數字型號 (如 m720, ps5, rtx4070, 128g)
        tokens = set(re.findall(r"[a-z0-9\+\-]+", c))
        # 中文 2~4 字詞
        chinese = re.findall(r"[\u4e00-\u9fff]{2,4}", c)
        tokens.update(chinese)
        return tokens

    @classmethod
    def calculate_similarity(cls, title1: str, title2: str) -> float:
        t1 = cls.extract_core_tokens(title1)
        t2 = cls.extract_core_tokens(title2)
        if not t1 or not t2:
            return 0.0
        
        # 若包含核心英數型號 (如 m720, ps5, switch, rtx) 且兩者皆有，大幅加權
        common = t1.intersection(t2)
        has_model_match = any(re.match(r"[a-z]+[0-9]+|[0-9]+[a-z]+|[a-z]{2,}", tok) for tok in common if len(tok) >= 3)
        if has_model_match:
            return 0.8  # 高度判定為同型號

        union = t1.union(t2)
        return len(common) / len(union) if union else 0.0

    @classmethod
    def group_similar_products(cls, items: List[ProductItem], similarity_threshold: float = 0.35) -> List[ComparisonGroup]:
        """將同一型號或同款商品精準歸納至同一個比價大區塊"""
        valid_items = [it for it in items if it.price > 0]
        if not valid_items:
            return []

        clusters: List[List[ProductItem]] = []

        for item in valid_items:
            assigned = False
            for cluster in clusters:
                # 檢查與 cluster 內任一代表性商品的相似度
                if any(cls.calculate_similarity(item.title, rep.title) >= similarity_threshold for rep in cluster[:3]):
                    cluster.append(item)
                    assigned = True
                    break
            if not assigned:
                clusters.append([item])

        # 整理比價群組
        comparison_groups: List[ComparisonGroup] = []
        for idx, group_items in enumerate(clusters):
            sorted_items = sorted(group_items, key=lambda x: x.price)
            lowest_item = sorted_items[0]
            highest_item = sorted_items[-1]
            
            lowest_p = lowest_item.price
            highest_p = highest_item.price
            diff = highest_p - lowest_p
            diff_percent = round((diff / highest_p) * 100, 1) if highest_p > 0 else 0.0

            platforms = list(set([it.platform for it in group_items]))
            
            # 取最乾淨俐落的代表標題
            titles = [cls.clean_title(it.title) for it in group_items if len(cls.clean_title(it.title)) > 4]
            normalized_title = min(titles, key=len) if titles else cls.clean_title(lowest_item.title) or lowest_item.title

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

        # 依據商品豐富度 (商品件數多者優先) 排序，把最重要的聚合大卡片排在最上面！
        comparison_groups.sort(key=lambda g: (len(g.items), len(g.platforms_available), g.price_diff_percent), reverse=True)
        return comparison_groups
