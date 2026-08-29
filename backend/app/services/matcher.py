import re
from typing import List, Set, Dict
from app.models.product import ProductItem, ComparisonGroup

class ProductMatcher:
    """智慧商品標題正規化、嚴格關聯度過濾與跨平台同款比價聚合器"""

    # 中英文品牌與同義詞對照庫
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

    # 廣告噪音符號
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
        return re.sub(r"\s+", " ", cleaned).strip()

    @classmethod
    def is_relevant(cls, title: str, query: str) -> bool:
        """嚴格驗證商品標題與使用者關鍵字意圖是否高度相關"""
        t_lower = title.lower()
        q_lower = query.lower().strip()
        if not q_lower:
            return True

        # 分解搜尋關鍵字詞 (例如 ['makita', '無線', '打蠟機'])
        raw_tokens = [tok for tok in re.split(r"[\s\+\-_/]+", q_lower) if tok]
        if not raw_tokens:
            return True

        # 1. 核心品牌/型號強制匹配 (如使用者輸入 makita，標題必須包含 makita 或 牧田)
        for tok in raw_tokens:
            if tok in cls.BRAND_SYNONYMS:
                syns = cls.BRAND_SYNONYMS[tok]
                if not any(s in t_lower for s in syns):
                    return False
            elif re.match(r"^[a-z0-9\+\-]+$", tok) and len(tok) >= 3:
                # 英文/型號代碼 (如 m720, rtx4070, ps5, oled)
                if tok not in t_lower and tok.replace("-", "") not in t_lower.replace("-", ""):
                    return False

        # 2. 關鍵字覆蓋率計算
        matched_score = 0.0
        for tok in raw_tokens:
            if tok in cls.BRAND_SYNONYMS:
                if any(s in t_lower for s in cls.BRAND_SYNONYMS[tok]):
                    matched_score += 1.0
            elif tok in t_lower:
                matched_score += 1.0
            elif len(tok) >= 2:
                # 中文字詞部分命中檢查 (如「打蠟機」命中「打蠟」或「拋光」)
                sub_matched = sum(1 for ch in tok if ch in t_lower) / len(tok)
                if sub_matched >= 0.5:
                    matched_score += sub_matched

        coverage = matched_score / len(raw_tokens)

        # 3. 避免配件/耗材干擾主機搜尋 (若使用者搜尋含「機」、「手機」、「滑鼠」、「電腦」但沒搜「棉/布/貼」)
        if any(w in q_lower for w in ["機", "主機", "滑鼠", "筆電", "顯卡", "手機"]):
            is_accessory_query = any(acc in q_lower for acc in ["棉", "海綿", "海棉", "布", "盤", "貼", "膜", "殼", "套", "袋"])
            if not is_accessory_query:
                # 若搜尋主機，但標題純為「海綿」、「黏扣盤」、「上蠟棉」且未包含主機本體
                if any(acc in t_lower for acc in ["海綿", "海棉", "上蠟棉", "打蠟棉", "拋光布", "黏扣盤", "保護貼", "保護膜", "保護套", "防塵套"]):
                    # 檢查標題是否真正包含主機機器字眼
                    if not any(m in t_lower for m in ["打蠟機", "拋光機", "研磨機", "主機", "滑鼠", "筆電", "顯卡"]):
                        return False

        return coverage >= 0.65

    @classmethod
    def filter_relevant_products(cls, items: List[ProductItem], keyword: str) -> List[ProductItem]:
        """過濾掉與使用者搜尋關鍵字無關或無效的商品"""
        if not keyword.strip():
            return items
        return [it for it in items if cls.is_relevant(it.title, keyword)]

    @classmethod
    def group_similar_products(cls, items: List[ProductItem], keyword: str = "") -> List[ComparisonGroup]:
        """將相關商品統一聚合在同一個大比價卡片中"""
        # 1. 執行嚴格關聯度過濾
        relevant_items = cls.filter_relevant_products(items, keyword)
        valid_items = [it for it in relevant_items if it.price > 0]
        
        # 若過濾後無完全匹配，回退至至少有效價格商品
        if not valid_items and items:
            valid_items = [it for it in items if it.price > 0]

        if not valid_items:
            return []

        # 2. 依價格由低到高排序
        sorted_items = sorted(valid_items, key=lambda x: x.price)
        lowest_item = sorted_items[0]
        highest_item = sorted_items[-1]
        
        diff = highest_item.price - lowest_item.price
        diff_percent = round((diff / highest_item.price) * 100, 1) if highest_item.price > 0 else 0.0
        platforms = list(dict.fromkeys([it.platform for it in sorted_items]))

        # 生成比價卡片標題
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
