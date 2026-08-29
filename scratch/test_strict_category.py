import sys, os, asyncio
sys.path.insert(0, os.path.abspath('backend'))
sys.path.insert(0, os.path.abspath('.'))
if sys.platform == 'win32':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass

import re
from app.services.aggregator import aggregator

ACCESSORY_KEYWORDS = [
    "保護貼", "玻璃貼", "秒貼膜", "保護膜", "貼膜", "鋼化膜", "防窺膜",
    "手機殼", "保護殼", "保護套", "防摔殼", "皮套", "清水套", "收納包", "收納袋", "防塵塞", "防塵套",
    "支架", "展示架", "收納架", "手把架", "散熱架", "底座", "壁掛架",
    "海綿", "海棉", "上蠟棉", "打蠟棉", "拋光棉", "羊毛輪", "黏扣盤", "砂紙片", "砂紙張",
    "充電線", "傳輸線", "充電器", "快充線", "充電頭", "充電座",
    "鼠貼", "鼠腳", "滑鼠墊", "防滑貼", "手把套"
]

def strict_product_filter(title: str, query: str) -> bool:
    t_lower = title.lower()
    q_lower = query.lower().strip()
    
    # 1. 品牌強制匹配
    if "makita" in q_lower or "牧田" in q_lower:
        if "makita" not in t_lower and "牧田" not in t_lower:
            return False
            
    if "logitech" in q_lower or "羅技" in q_lower:
        if "logitech" not in t_lower and "羅技" not in t_lower:
            return False

    if "apple" in q_lower or "蘋果" in q_lower or "iphone" in q_lower or "ipad" in q_lower:
        if not any(k in t_lower for k in ["apple", "蘋果", "iphone", "ipad"]):
            return False

    if "sony" in q_lower or "索尼" in q_lower or "ps5" in q_lower:
        if not any(k in t_lower for k in ["sony", "索尼", "ps5", "playstation"]):
            return False

    # 2. 規格/型號強制匹配 (如 40v, 18v, m720, rtx4070, ps5, slim)
    specs = re.findall(r"\b\d+v\b|[a-z]+\d+|\d+[a-z]+|slim|pro|oled", q_lower)
    for sp in specs:
        if sp not in t_lower:
            return False

    # 3. 核心品類名詞匹配與衝突排除
    if "砂紙機" in q_lower or "砂光機" in q_lower or "磨砂機" in q_lower:
        if not any(k in t_lower for k in ["砂紙", "砂光", "磨砂", "打磨", "砂輪", "sander"]):
            return False
        if any(bad in t_lower for bad in ["電鑽", "起子", "震動機", "鏈鋸", "割草", "吹風機", "水泥震動"]):
            return False

    if "打蠟機" in q_lower or "拋光機" in q_lower:
        if not any(k in t_lower for k in ["打蠟", "打臘", "拋光", "鍍膜"]):
            return False
        if any(bad in t_lower for bad in ["電鑽", "起子", "鏈鋸", "砂紙", "割草"]):
            return False

    # 4. 配件/耗材智慧過濾 (若使用者未明確搜尋配件名詞，排除純配件/貼膜/保護殼/支架)
    is_acc_query = any(acc in q_lower for acc in ACCESSORY_KEYWORDS)
    if not is_acc_query:
        # 如果使用者搜尋主機 (iPhone, PS5, 滑鼠, 打蠟機, 砂紙機...)
        if any(acc in t_lower for acc in ACCESSORY_KEYWORDS):
            # 檢查標題是否「主要」是配件而不是主機本體
            # 若標題含有「保護貼」、「秒貼膜」、「主機防塵塞」、「手把支架」、「鼠貼」、「單電池」等
            if not any(main in t_lower for main in ["手機", "主機", "盒裝", "原廠主機", "公司貨主機", "單主機", "全套"]):
                return False
            # 針對 iPhone 貼膜
            if any(film in t_lower for film in ["秒貼膜", "玻璃貼", "鋼化膜", "防窺膜", "保護貼", "防塵塞", "手把支架", "鼠貼"]):
                return False

    return True

async def test():
    for q in ["makita 40v 無線砂紙機", "PS5 Slim", "iPhone 16", "羅技 M720"]:
        res = await aggregator.search(q, use_cache=False)
        passed = [it for it in res.results if strict_product_filter(it.title, q)]
        print(f"\n=== Query: {q} (Raw: {res.total_found} -> Passed: {len(passed)}) ===")
        for it in passed[:3]:
            print(f"  - [{it.platform}] NT$ {it.price} | {it.title[:50]}")

asyncio.run(test())
