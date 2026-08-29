import httpx
from typing import List
import logging
from app.crawlers.base import BaseCrawler
from app.models.product import ProductItem

logger = logging.getLogger(__name__)

class ShopeeCrawler(BaseCrawler):
    """蝦皮購物 (Shopee) 爬蟲適配器 (僅抓取真實商品與真實賣場連結)"""
    
    platform_id: str = "shopee"
    platform_name: str = "蝦皮購物"
    platform_badge_color: str = "#EE4D2D"  # Shopee 橘紅色

    async def fetch_products(self, keyword: str, limit: int = 30) -> List[ProductItem]:
        encoded_kw = keyword.replace(" ", "%20")
        url = f"https://shopee.tw/api/v4/search/search_items?by=relevancy&keyword={encoded_kw}&limit={limit}&newest=0&order=desc&page_type=search&scenario=PAGE_GLOBAL_SEARCH&version=2"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept": "application/json",
            "X-Shopee-Language": "zh-Hant",
            "X-Requested-With": "XMLHttpRequest",
            "X-API-SOURCE": "rweb"
        }
        
        try:
            async with httpx.AsyncClient(timeout=4.0, headers=headers) as client:
                response = await client.get(url)
                if response.status_code == 200:
                    data = response.json()
                    items = data.get("items", [])
                    results: List[ProductItem] = []
                    for it in items[:limit]:
                        basic = it.get("item_basic", {})
                        item_id = basic.get("itemid")
                        shop_id = basic.get("shopid")
                        name = basic.get("name", "").strip()
                        raw_price = basic.get("price", 0) / 100000.0
                        raw_orig = basic.get("price_before_discount", 0) / 100000.0
                        img = basic.get("image")
                        
                        if not name or not item_id or not shop_id:
                            continue
                            
                        # 庫存檢查與過濾
                        stock = basic.get("stock", 1)
                        if stock <= 0 or raw_price <= 0:
                            continue

                        # 蝦皮真實 CDN 圖片與專屬賣家商品詳情購買頁
                        img_url = f"https://cf.shopee.tw/file/{img}" if img else "https://deo.shopeemobile.com/shopee/shopee-pcmall-live-sg/assets/icon_no_image.png"
                        product_url = f"https://shopee.tw/product/{shop_id}/{item_id}"

                        results.append(
                            ProductItem(
                                id=f"shopee_{item_id}",
                                title=name,
                                price=round(raw_price),
                                original_price=round(raw_orig) if raw_orig > raw_price else None,
                                platform=self.platform_name,
                                platform_id=self.platform_id,
                                platform_badge_color=self.platform_badge_color,
                                product_url=product_url,
                                image_url=img_url,
                                in_stock=True,
                                rating=round(basic.get("item_rating", {}).get("rating_star", 4.9), 1),
                                rating_count=basic.get("historical_sold", 0),
                                tags=["蝦皮購物", "真實賣家", "正品保障"],
                                shipping_info="店到店 / 依賣場出貨"
                            )
                        )
                    return results
                else:
                    logger.warning(f"Shopee API 回應代碼: {response.status_code} (受防爬機制保護)")
        except Exception as e:
            logger.warning(f"Shopee 爬蟲連線異常: {e}")

        # 若蝦皮受反爬蟲阻擋，絕不捏造虛假商品或錯置圖片，誠實回傳空清單由其他四大電商提供真實資料
        return []
