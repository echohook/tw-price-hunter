import httpx
from typing import List
import logging
from app.crawlers.base import BaseCrawler
from app.models.product import ProductItem

logger = logging.getLogger(__name__)

class PChomeCrawler(BaseCrawler):
    """PChome 24h 線上購物爬蟲適配器 (支援缺貨過濾)"""
    
    platform_id: str = "pchome"
    platform_name: str = "PChome 24h"
    platform_badge_color: str = "#E03A3E"  # PChome 紅色

    async def fetch_products(self, keyword: str, limit: int = 30) -> List[ProductItem]:
        url = "https://ecshweb.pchome.com.tw/search/v3.3/all/results"
        params = {
            "q": keyword,
            "page": 1,
            "sort": "rnk/dc"
        }
        
        async with httpx.AsyncClient(timeout=self.timeout, headers=self.headers, follow_redirects=True) as client:
            response = await client.get(url, params=params)
            if response.status_code != 200:
                logger.error(f"PChome 回應狀態碼異常: {response.status_code}")
                return []
            
            data = response.json()
            prods = data.get("prods", [])
            
            results: List[ProductItem] = []
            for item in prods[:limit]:
                # 缺貨與下架狀態判斷
                is_sold_out = item.get("isSoldOut") == 1 or item.get("button") == "售完" or str(item.get("stock", "1")) == "0"
                if is_sold_out:
                    continue

                prod_id = item.get("Id", "")
                name = item.get("name", "")
                price = self.clean_price(item.get("price"))
                if price <= 0:
                    continue
                    
                origin_price = self.clean_price(item.get("originPrice")) if item.get("originPrice") else None
                
                # PChome 圖片路徑規格
                pic_b = item.get("picB", "")
                pic_s = item.get("picS", "")
                img_path = pic_b or pic_s
                if img_path.startswith("http"):
                    image_url = img_path
                elif img_path:
                    image_url = f"https://cs-a.ecimg.tw{img_path}"
                else:
                    image_url = "https://24h.pchome.com.tw/assets/images/no-image.png"
                
                # 商品原始購買頁網址
                product_url = f"https://24h.pchome.com.tw/prod/{prod_id}"
                
                tags = ["24h到貨"]
                if item.get("isCoupon"):
                    tags.append("折價券")
                if item.get("isInstallment"):
                    tags.append("分期0利率")
                
                results.append(
                    ProductItem(
                        id=f"pchome_{prod_id}",
                        title=name,
                        price=price,
                        original_price=origin_price if origin_price and origin_price > price else None,
                        platform=self.platform_name,
                        platform_id=self.platform_id,
                        platform_badge_color=self.platform_badge_color,
                        product_url=product_url,
                        image_url=image_url,
                        in_stock=True,
                        rating=4.8,
                        tags=tags,
                        shipping_info="滿$490免運 / 24小時快速到貨"
                    )
                )
            
            return results
