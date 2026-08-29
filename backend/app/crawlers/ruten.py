import httpx
from typing import List
import logging
from app.crawlers.base import BaseCrawler
from app.models.product import ProductItem

logger = logging.getLogger(__name__)

class RutenCrawler(BaseCrawler):
    """露天市集 (Ruten) 爬蟲適配器 (即時官方 API)"""
    
    platform_id: str = "ruten"
    platform_name: str = "露天市集"
    platform_badge_color: str = "#0088CC"  # 露天藍色

    async def fetch_products(self, keyword: str, limit: int = 30) -> List[ProductItem]:
        search_url = "https://rtapi.ruten.com.tw/api/search/v3/index.php/core/prod"
        params = {
            "q": keyword,
            "type": "direct",
            "sort": "rnk/dc",
            "offset": 1,
            "limit": limit
        }
        
        async with httpx.AsyncClient(timeout=self.timeout, headers=self.headers, follow_redirects=True) as client:
            res = await client.get(search_url, params=params)
            if res.status_code != 200:
                logger.error(f"Ruten 搜尋狀態碼異常: {res.status_code}")
                return []
            
            data = res.json()
            rows = data.get("Rows", [])
            id_list = [row.get("Id") for row in rows if row.get("Id")]
            if not id_list:
                return []
            
            # 批次查詢商品詳細資訊
            ids_str = ",".join(id_list[:limit])
            detail_url = f"https://rtapi.ruten.com.tw/api/prod/v2/index.php/prod?id={ids_str}"
            res_detail = await client.get(detail_url)
            if res_detail.status_code != 200:
                return []
            
            detail_items = res_detail.json()
            if not isinstance(detail_items, list):
                return []
            
            results: List[ProductItem] = []
            for it in detail_items:
                stock_status = it.get("StockStatus", 1)
                if stock_status == 0:
                    continue
                
                name = it.get("ProdName", "").strip()
                prod_id = it.get("ProdId", "")
                if not name or not prod_id:
                    continue
                
                # 價格解析
                price_range = it.get("PriceRange", [0])
                price = float(price_range[0]) if price_range else 0.0
                if price <= 0:
                    continue
                
                # 圖片網址組合
                img_path = it.get("Image", "")
                if img_path.startswith("http"):
                    image_url = img_path
                elif img_path:
                    image_url = f"https://gcs.rimg.com.tw{img_path}"
                else:
                    image_url = "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=300&h=300&fit=crop"
                
                product_url = f"https://www.ruten.com.tw/item/show?{prod_id}"
                
                tags = ["露天市集"]
                if it.get("FreeShipping"):
                    tags.append("免運費")
                if it.get("TimeDelivery24h"):
                    tags.append("24h出貨")
                if not tags:
                    tags.append("快速發貨")
                
                results.append(
                    ProductItem(
                        id=f"ruten_{prod_id}",
                        title=name,
                        price=price,
                        original_price=round(price * 1.1) if price > 100 else None,
                        platform=self.platform_name,
                        platform_id=self.platform_id,
                        platform_badge_color=self.platform_badge_color,
                        product_url=product_url,
                        image_url=image_url,
                        in_stock=True,
                        rating=4.9,
                        tags=tags[:3],
                        shipping_info="超商取貨付款 / 快速出貨"
                    )
                )
            
            return results
