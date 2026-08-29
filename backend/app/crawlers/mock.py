import random
from typing import List
from app.crawlers.base import BaseCrawler
from app.models.product import ProductItem

class MockCrawler(BaseCrawler):
    """離線/單元測試專用模擬爬蟲"""
    
    platform_id: str = "mock"
    platform_name: str = "測試商城 (Mock)"
    platform_badge_color: str = "#6B7280"

    async def fetch_products(self, keyword: str, limit: int = 10) -> List[ProductItem]:
        results: List[ProductItem] = []
        base_price = 1000.0 if "衛生紙" in keyword else 25000.0
        
        for i in range(1, limit + 1):
            price_variance = random.uniform(0.85, 1.15)
            price = round(base_price * price_variance)
            orig_price = round(price * 1.2)
            
            results.append(
                ProductItem(
                    id=f"mock_{i}_{random.randint(1000, 9999)}",
                    title=f"[展示商品] {keyword} 高品質旗艦款 (規格 {i})",
                    price=float(price),
                    original_price=float(orig_price),
                    platform=self.platform_name,
                    platform_id=self.platform_id,
                    platform_badge_color=self.platform_badge_color,
                    product_url=f"https://example.com/product/{i}",
                    image_url="https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=300&h=300&fit=crop",
                    in_stock=True,
                    rating=4.8,
                    rating_count=50 + i * 10,
                    tags=["快速出貨", "滿千免運"],
                    shipping_info="全館免運"
                )
            )
        return results
