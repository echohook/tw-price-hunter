import re
from typing import List, Set, Dict
from app.models.product import ProductItem, ComparisonGroup

class ProductMatcher:
    """智慧商品標題正規化、嚴格品類與規格匹配器"""

    # 中英文品牌與同義詞庫
    BRAND_SYNONYMS: Dict[str, List[str]] = {
        "makita": ["makita", "牧田"],
        "牧田": ["makita", "牧田"],
        "bosch": ["bosch", "博世"],
        "博世": ["bosch", "博世"],
        "dewalt": ["dewalt", "得偉"],
        "得偉": ["dewalt", "得偉"],
        "milwaukee": ["milwaukee", "美沃奇", "米沃奇"],
        "logitech": ["logitech", "羅技"],
        "羅技": ["logitech", "羅技"],
        "apple": ["apple", "蘋果", "iphone", "ipad", "macbook", "airpods"],
        "蘋果": ["apple", "蘋果", "iphone", "ipad", "macbook", "airpods"],
        "sony": ["sony", "索尼", "ps5", "playstation"],
        "索尼": ["sony", "索尼", "ps5", "playstation"],
        "asus": ["asus", "華碩", "rog", "tuf"],
        "華碩": ["asus", "華碩", "rog", "tuf"],
        "msi": ["msi", "微星"],
        "微星": ["msi", "微星"],
        "gigabyte": ["gigabyte", "技嘉", "aorus"],
        "技嘉": ["gigabyte", "技嘉", "aorus"],
        "dyson": ["dyson", "戴森"],
        "戴森": ["dyson", "戴森"],
        "panasonic": ["panasonic", "國際牌", "松下"],
        "國際牌": ["panasonic", "國際牌", "松下"],
        "samsung": ["samsung", "三星", "galaxy"],
        "三星": ["samsung", "三星", "galaxy"],
        "spring": ["春風"],
        "春風": ["春風"],
        "kleenex": ["舒潔"],
        "舒潔": ["舒潔"],
    }

    # 配件與耗材關鍵字
    ACCESSORY_KEYWORDS = [
        "保護貼", "玻璃貼", "秒貼膜", "保護膜", "貼膜", "鋼化膜", "防窺膜",
        "防塵塞", "防塵套", "散熱架", "手把架", "底座", "收納架",
        "海綿", "海棉", "上蠟棉", "打蠟棉", "拋光棉", "羊毛輪", "黏扣盤",
        "充電線", "傳輸線", "快充線", "鼠貼", "鼠腳"
    ]

    # 品類衝突與強制詞庫
    CATEGORY_RULES = {
        "砂紙機": {
            "required": ["砂紙", "砂光", "磨砂", "打磨", "砂輪", "sander"],
            "forbidden": ["電鑽", "起子", "震動機", "鏈鋸", "割草", "吹風機", "水泥震動", "純電池"]
        },
        "打蠟機": {
            "required": ["打蠟", "打臘", "拋光", "鍍膜", "polisher", "buffer"],
            "forbidden": ["電鑽", "起子", "鏈鋸", "砂紙", "割草", "水泥震動"]
        },
        "電鑽": {
            "required": ["電鑽", "起子", "衝擊鑽", "drill"],
            "forbidden": ["鏈鋸", "打蠟", "砂紙", "割草", "吹風機"]
        },
        "衛生紙": {
            "required": ["衛生紙", "面紙", "抽取式", "平板", "紙巾", "tissue"],
            "forbidden": ["手錶", "墨鏡", "滑鼠", "顯卡"]
        },
        "滑鼠": {
            "required": ["滑鼠", "鼠標", "mouse"],
            "forbidden": ["耳機", "墨鏡", "衛生紙"]
        }
    }

    # 廣告噪音符號
    NOISE_PATTERNS = [
        r"【.*?】", r"\[.*?\]", r"\(.*?\)", r"（.*?）", r"★.*?★", r"◆.*?◆", r"▼.*?▼",
        r"📣|❤️|🔥|⭐|✨|⚡|💥|👉|✔️|🏆|💎",
        r"\b(現貨|公司貨|原廠|官方|旗艦|熱銷|熱賣|特惠|下殺|狂降|免運|正品|保固|24h|速達|含發票|開發票|附發票|店到店|超商|秒出|兩年保固|一年保固|原廠盒裝|台灣公司貨|全新|二手|9成新|95成新|福利品|出清|展示品)\b",
        r"送.*?元", r"限時.*?", r"滿.*?(折|送|折抵)",
    ]

    @classmethod
    def clean_title(cls, title: str) -> str:
        cleaned = title
        for pattern in cls.NOISE_PATTERNS:
            cleaned = re.sub(pattern, " ", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"[^\w\s\.\-\+]", " ", cleaned)
        return re.sub(r"\s+", " ", cleaned).strip()

    @classmethod
    def is_relevant(cls, title: str, query: str) -> bool:
        t_lower = title.lower()
        q_lower = query.lower().strip()
        if not q_lower:
            return True

        # 1. 品牌強制匹配 (如 makita 必須包含 makita 或 牧田)
        for b_key, syns in cls.BRAND_SYNONYMS.items():
            if b_key in q_lower:
                if not any(s in t_lower for s in syns):
                    return False

        # 2. 規格/電壓/型號強制匹配 (如 40v, 18v, 12v, m720, rtx4070)
        specs = re.findall(r"\b\d+v\b|[a-z]+\d+|\d+[a-z]+", q_lower)
        for sp in specs:
            if sp not in t_lower and sp.replace("-", "") not in t_lower.replace("-", ""):
                return False

        # 3. 核心品類名詞匹配與衝突排除 (如搜 砂紙機 絕不允許 電鑽, 鏈鋸, 水泥震動機)
        for cat_name, rules in cls.CATEGORY_RULES.items():
            if cat_name in q_lower or any(req in q_lower for req in rules["required"]):
                # 標題必須包含該品類核心詞
                if not any(req in t_lower for req in rules["required"]):
                    return False
                # 且絕不允許衝突品類字眼 (如鏈鋸, 電鑽)
                if any(forb in t_lower for forb in rules["forbidden"]) and not any(req in t_lower for req in rules["required"][:2]):
                    return False

        # 4. 配件耗材過濾 (若搜機器但標題只是純海綿、貼膜或純電池)
        is_acc_query = any(acc in q_lower for acc in cls.ACCESSORY_KEYWORDS)
        if not is_acc_query:
            if any(acc in t_lower for acc in cls.ACCESSORY_KEYWORDS):
                if not any(main in t_lower for main in ["主機", "單主機", "套裝", "手機", "滑鼠", "筆電", "顯卡"]):
                    return False
                if any(film in t_lower for film in ["秒貼膜", "玻璃貼", "鋼化膜", "防窺膜", "保護貼", "防塵塞", "手把架"]):
                    return False

        # 5. 純電池過濾 (若搜主機機器但標題純為副廠電池)
        if any(m in q_lower for m in ["機", "滑鼠", "手機"]) and not any(b in q_lower for b in ["電池", "充電"]):
            if ("電池" in t_lower or "充電座" in t_lower) and not any(m in t_lower for m in ["砂紙機", "砂光機", "打蠟機", "主機", "單主機", "套裝"]):
                return False

        return True

    @classmethod
    def filter_relevant_products(cls, items: List[ProductItem], keyword: str) -> List[ProductItem]:
        if not keyword.strip():
            return items
        filtered = [it for it in items if cls.is_relevant(it.title, keyword)]
        return filtered if filtered else [it for it in items if it.price > 0]

    @classmethod
    def group_similar_products(cls, items: List[ProductItem], keyword: str = "") -> List[ComparisonGroup]:
        relevant_items = cls.filter_relevant_products(items, keyword)
        valid_items = [it for it in relevant_items if it.price > 0]
        if not valid_items:
            return []

        sorted_items = sorted(valid_items, key=lambda x: x.price)
        lowest_item = sorted_items[0]
        highest_item = sorted_items[-1]
        
        diff = highest_item.price - lowest_item.price
        diff_percent = round((diff / highest_item.price) * 100, 1) if highest_item.price > 0 else 0.0
        platforms = list(dict.fromkeys([it.platform for it in sorted_items]))

        clean_kw = keyword.strip()
        group_title = f"「{clean_kw}」跨平台比價與各賣家報價清單" if clean_kw else (cls.clean_title(lowest_item.title) or lowest_item.title)

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
