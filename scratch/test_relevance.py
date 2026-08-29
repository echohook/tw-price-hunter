import sys, os, asyncio
sys.path.insert(0, os.path.abspath('backend'))
if sys.platform == 'win32':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass

import re
from app.services.aggregator import aggregator

# 品牌與關鍵詞同義字對照表
SYNONYMS = {
    "makita": ["makita", "牧田"],
    "logitech": ["logitech", "羅技"],
    "apple": ["apple", "蘋果", "iphone", "ipad", "macbook"],
    "sony": ["sony", "索尼", "ps5", "playstation"],
    "asus": ["asus", "華碩"],
    "msi": ["msi", "微星"],
    "gigabyte": ["gigabyte", "技嘉"],
    "dyson": ["dyson", "戴森"],
    "panasonic": ["panasonic", "國際牌", "松下"],
    "spring": ["春風"],
}

def is_relevant(title: str, query: str) -> bool:
    t_lower = title.lower()
    q_lower = query.lower()
    
    # 分解搜尋關鍵字詞
    tokens = [tok for tok in re.split(r"[\s\+\-_/]+", q_lower) if tok]
    if not tokens:
        return True

    # 檢查每個詞彙是否在標題中（包含同義字匹配）
    matched_count = 0
    for tok in tokens:
        # 同義詞檢查 (如 makita -> 牧田)
        syns = SYNONYMS.get(tok, [tok])
        if any(s in t_lower for s in syns):
            matched_count += 1
        elif len(tok) >= 2:
            # 針對中文字詞，檢查子字串 (例如 打蠟機 -> 打蠟 or 拋光)
            if any(ch in t_lower for ch in tok) and ("打蠟" in t_lower or "拋光" in t_lower or "洗車" in t_lower):
                matched_count += 0.8

    match_ratio = matched_count / len(tokens)
    
    # 若搜尋字詞中有明確品牌或英文型號，必須強匹配
    for tok in tokens:
        if re.match(r"^[a-z0-9]+$", tok) and len(tok) >= 3:
            syns = SYNONYMS.get(tok, [tok])
            if not any(s in t_lower for s in syns):
                return False  # 缺關鍵品牌/型號，直接判定無關排除

    return match_ratio >= 0.7

async def test():
    # 測試 makita 無線打蠟機
    res = await aggregator.search("makita 無線打蠟機", use_cache=False)
    print(f"Raw items count: {res.total_found}")
    
    filtered = [it for it in res.results if is_relevant(it.title, "makita 無線打蠟機")]
    print(f"Relevant items count: {len(filtered)}")
    print("\nTop 8 relevant items:")
    for it in filtered[:8]:
        print(f"[{it.platform}] NT$ {it.price} | {it.title[:45]}")

asyncio.run(test())
