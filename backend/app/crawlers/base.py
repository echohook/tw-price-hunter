from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
import time
import httpx
import logging
from app.models.product import ProductItem

logger = logging.getLogger(__name__)

class BaseCrawler(ABC):
    """電商爬蟲抽象基底類別 (Adapter Interface)"""
    
    platform_id: str = "base"
    platform_name: str = "Base Platform"
    platform_badge_color: str = "gray"
    default_timeout: float = 10.0

    def __init__(self, timeout: Optional[float] = None):
        self.timeout = timeout or self.default_timeout
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        }

    @abstractmethod
    async def fetch_products(self, keyword: str, limit: int = 30) -> List[ProductItem]:
        """抓取電商商品清單的核心抽象方法"""
        pass

    async def search(self, keyword: str, limit: int = 30) -> Tuple[List[ProductItem], float, Optional[str]]:
        """帶有計時與容錯處理的公開搜尋方法"""
        start_time = time.time()
        keyword = keyword.strip()
        if not keyword:
            return [], 0.0, None
            
        try:
            items = await self.fetch_products(keyword, limit=limit)
            elapsed_ms = (time.time() - start_time) * 1000
            return items, elapsed_ms, None
        except Exception as e:
            elapsed_ms = (time.time() - start_time) * 1000
            error_msg = f"{self.platform_name} 抓取失敗: {str(e)}"
            logger.warning(error_msg)
            return [], elapsed_ms, error_msg

    def clean_price(self, price_val: any) -> float:
        """價格字串正規化為浮點數"""
        if price_val is None:
            return 0.0
        if isinstance(price_val, (int, float)):
            return float(price_val)
        
        # 清除錢字號、逗號與多餘文字
        s = str(price_val).replace("$", "").replace("NT", "").replace(",", "").strip()
        try:
            return float(s)
        except ValueError:
            import re
            m = re.search(r"(\d+(\.\d+)?)", s)
            if m:
                return float(m.group(1))
            return 0.0
