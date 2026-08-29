import httpx
import json
from typing import List
import logging
from app.crawlers.base import BaseCrawler
from app.models.product import ProductItem

logger = logging.getLogger(__name__)

class MomoCrawler(BaseCrawler):
    """Momo 購物網爬蟲適配器 (支援 B2C 與 mo店+ 商店街與即時庫存過濾)"""
    
    platform_id: str = "momo"
    platform_name: str = "Momo 購物網"
    platform_badge_color: str = "#E6007E"  # Momo 粉桃紅

    async def fetch_products(self, keyword: str, limit: int = 30) -> List[ProductItem]:
        url = "https://www.momoshop.com.tw/search/searchShop.jsp"
        params = {
            "keyword": keyword,
            "searchType": "1",
            "curPage": "1",
            "_isFuzzy": "0",
            "showType": "chessboardType"
        }
        
        async with httpx.AsyncClient(
            timeout=self.timeout,
            headers=self.headers,
            verify=False,
            follow_redirects=True
        ) as client:
            response = await client.get(url, params=params)
            if response.status_code != 200:
                logger.error(f"Momo 回應狀態碼異常: {response.status_code}")
                return []
            
            html = response.text
            
            # 從 Momo Next.js 串流狀態中解析 goodsInfoList
            idx = html.find("goodsInfoList")
            if idx == -1:
                logger.info("Momo 頁面未找到 goodsInfoList 區塊")
                return []
            
            start_bracket = html.find("[", idx)
            if start_bracket == -1:
                return []
            
            # 括號配對法提取 JSON 陣列
            count = 0
            end_bracket = -1
            in_str = False
            escape = False
            for i in range(start_bracket, len(html)):
                char = html[i]
                if escape:
                    escape = False
                    continue
                if char == "\\":
                    escape = True
                    continue
                if char == '"':
                    in_str = not in_str
                    continue
                if not in_str:
                    if char == "[":
                        count += 1
                    elif char == "]":
                        count -= 1
                        if count == 0:
                            end_bracket = i
                            break
            
            if end_bracket == -1:
                return []
            
            raw_json = html[start_bracket:end_bracket+1]
            cleaned = raw_json.replace('\\"', '"').replace('\\\\', '\\')
            
            try:
                raw_items = json.loads(cleaned)
            except Exception as e:
                logger.warning(f"Momo JSON 解析失敗: {e}")
                return []
            
            results: List[ProductItem] = []
            for item in raw_items[:limit]:
                goods_code = str(item.get("goodsCode", "")).strip()
                name = item.get("goodsName", "").strip()
                if not name or not goods_code:
                    continue
                
                # 庫存與缺貨狀態判斷 (過濾無貨/熱銷一空商品)
                stock_val = str(item.get("goodsStock", "1")).strip()
                is_sold_out = item.get("isSoldOut") == "1"
                can_tip_stock = item.get("canTipStock") == "Y"  # 缺貨補貨中
                
                # 若庫存為 0 或已售完，則判定為無庫存
                if stock_val == "0" or is_sold_out or can_tip_stock:
                    continue
                
                price = self.clean_price(item.get("goodsPrice"))
                if price <= 0:
                    continue
                    
                origin_price_raw = item.get("goodsPriceOri") or item.get("marketPriceModel", {}).get("basePrice", {}).get("price")
                origin_price = self.clean_price(origin_price_raw) if origin_price_raw else None
                
                # 處理商品詳情網址 (區分 B2C 與 mo店+ TP 商店商品)
                if goods_code.startswith("TP"):
                    entp = item.get("action", {}).get("extraValue", {}).get("entpCode") or goods_code[:9]
                    product_url = f"https://www.momoshop.com.tw/TP/{entp}/goodsDetail/{goods_code}"
                    is_mo_store = True
                else:
                    product_url = f"https://www.momoshop.com.tw/goods/GoodsDetail.jsp?i_code={goods_code}"
                    is_mo_store = False
                
                # Momo 圖片網址組合規格
                image_url = item.get("imgUrl") or item.get("goodsImgUrl")
                if not image_url:
                    if goods_code.startswith("TP"):
                        image_url = f"https://i8.momoshop.com.tw/goodsimg/{goods_code[:5]}/{goods_code[5:9]}/{goods_code[9:13]}/{goods_code[13:]}/{goods_code}_O_m.jpg"
                    else:
                        padded = goods_code.zfill(10)
                        image_url = f"https://img4.momoshop.com.tw/goodsimg/{padded[:4]}/{padded[4:7]}/{padded[7:]}/{goods_code}_R.jpg"
                
                # 標籤與庫存
                tags = ["mo店+" if is_mo_store else "Momo速達"]
                if item.get("useCounpon") == "1":
                    tags.append("折價券")
                if item.get("haveGift") == "1":
                    tags.append("送贈品")
                if item.get("isDiscount") == "1":
                    tags.append("特價促銷")
                
                results.append(
                    ProductItem(
                        id=f"momo_{goods_code}",
                        title=name,
                        price=price,
                        original_price=origin_price if origin_price and origin_price > price else None,
                        platform=self.platform_name,
                        platform_id=self.platform_id,
                        platform_badge_color=self.platform_badge_color,
                        product_url=product_url,
                        image_url=image_url,
                        in_stock=True,
                        rating=4.9,
                        tags=tags,
                        shipping_info="滿$490免運 / 快速配送"
                    )
                )
            
            return results
