import asyncio
import time
from typing import List, Dict, Type, Optional
import logging

from app.models.product import (
    ProductItem,
    SearchResponse,
    PlatformStatus,
    ComparisonGroup
)
from app.crawlers.base import BaseCrawler
from app.crawlers.pchome import PChomeCrawler
from app.crawlers.momo import MomoCrawler
from app.crawlers.yahoo import YahooCrawler
from app.crawlers.shopee import ShopeeCrawler
from app.crawlers.ruten import RutenCrawler
from app.crawlers.mock import MockCrawler
from app.services.cache import search_cache
from app.services.matcher import ProductMatcher
from app.config import settings

logger = logging.getLogger(__name__)

class PriceAggregator:
    """跨平台比價調度與聚合核心引擎 (支援動態外掛註冊)"""

    def __init__(self):
        # 註冊所有可用電商爬蟲適配器
        self._crawlers: Dict[str, BaseCrawler] = {
            "pchome": PChomeCrawler(),
            "momo": MomoCrawler(),
            "yahoo": YahooCrawler(),
            "ruten": RutenCrawler(),
            "shopee": ShopeeCrawler(),
            "mock": MockCrawler(),
        }

    def register_crawler(self, crawler: BaseCrawler):
        """外掛式註冊新電商爬蟲 (例如 Coupang, Books, etc.)"""
        self._crawlers[crawler.platform_id] = crawler
        logger.info(f"已成功註冊新電商適配器: {crawler.platform_name} ({crawler.platform_id})")

    def get_supported_platforms(self) -> List[Dict[str, str]]:
        return [
            {
                "id": c.platform_id,
                "name": c.platform_name,
                "color": c.platform_badge_color
            }
            for c in self._crawlers.values()
            if c.platform_id != "mock"
        ]

    async def search(
        self,
        keyword: str,
        platforms: Optional[List[str]] = None,
        sort_by: str = "price_asc",
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        use_cache: bool = True
    ) -> SearchResponse:
        """非同步並行搜尋多家電商並計算比價統計"""
        start_total_time = time.time()
        
        target_platform_ids = platforms or settings.DEFAULT_ENABLED_PLATFORMS
        # 篩選出系統有註冊的爬蟲
        active_crawlers = [
            self._crawlers[pid]
            for pid in target_platform_ids
            if pid in self._crawlers
        ]

        if not active_crawlers:
            active_crawlers = [self._crawlers["pchome"], self._crawlers["momo"], self._crawlers["yahoo"]]

        # 1. 檢查快取
        if use_cache:
            cached_res = search_cache.get(keyword, [c.platform_id for c in active_crawlers])
            if cached_res:
                return self._apply_filters_and_sort(cached_res, sort_by, min_price, max_price)

        # 2. 非同步並行調用各平台爬蟲
        tasks = [c.search(keyword, limit=settings.MAX_RESULTS_PER_PLATFORM) for c in active_crawlers]
        results_tuples = await asyncio.gather(*tasks, return_exceptions=True)

        all_items: List[ProductItem] = []
        platforms_status: List[PlatformStatus] = []
        platforms_searched: List[str] = []

        for crawler, result in zip(active_crawlers, results_tuples):
            platforms_searched.append(crawler.platform_name)
            if isinstance(result, Exception):
                platforms_status.append(
                    PlatformStatus(
                        platform_id=crawler.platform_id,
                        platform_name=crawler.platform_name,
                        is_active=False,
                        response_time_ms=0.0,
                        items_count=0,
                        error=str(result)
                    )
                )
            else:
                items, elapsed_ms, err = result
                platforms_status.append(
                    PlatformStatus(
                        platform_id=crawler.platform_id,
                        platform_name=crawler.platform_name,
                        is_active=(err is None and len(items) > 0),
                        response_time_ms=round(elapsed_ms, 1),
                        items_count=len(items),
                        error=err
                    )
                )
                all_items.extend([it for it in items if it.in_stock and it.price > 0])

        # 3. 最低價標籤標註與價差統計
        valid_prices = [item.price for item in all_items if item.price > 0]
        lowest_p = min(valid_prices) if valid_prices else 0.0
        highest_p = max(valid_prices) if valid_prices else 0.0
        avg_p = round(sum(valid_prices) / len(valid_prices), 1) if valid_prices else 0.0

        for item in all_items:
            if item.price > 0:
                item.is_lowest_price = (item.price == lowest_p)
                item.price_diff_with_lowest = round(item.price - lowest_p, 1)

        # 4. 同款商品分組與聚合
        comparison_groups = ProductMatcher.group_similar_products(all_items, keyword=keyword)

        total_exec_ms = round((time.time() - start_total_time) * 1000, 1)

        response = SearchResponse(
            keyword=keyword,
            total_found=len(all_items),
            lowest_price=lowest_p,
            average_price=avg_p,
            highest_price=highest_p,
            platforms_searched=platforms_searched,
            platforms_status=platforms_status,
            results=all_items,
            comparison_groups=comparison_groups,
            execution_time_ms=total_exec_ms,
            cached=False
        )

        # 5. 寫入快取
        if use_cache and len(all_items) > 0:
            search_cache.set(keyword, [c.platform_id for c in active_crawlers], response)

        return self._apply_filters_and_sort(response, sort_by, min_price, max_price)

    def _apply_filters_and_sort(
        self,
        res: SearchResponse,
        sort_by: str,
        min_price: Optional[float],
        max_price: Optional[float]
    ) -> SearchResponse:
        """套用價格區間篩選與排序規則"""
        filtered_results = list(res.results)

        if min_price is not None:
            filtered_results = [it for it in filtered_results if it.price >= min_price]
        if max_price is not None:
            filtered_results = [it for it in filtered_results if it.price <= max_price]

        # 排序
        if sort_by == "price_asc":
            filtered_results.sort(key=lambda x: (x.price == 0, x.price))
        elif sort_by == "price_desc":
            filtered_results.sort(key=lambda x: x.price, reverse=True)
        elif sort_by == "platform":
            filtered_results.sort(key=lambda x: x.platform)

        # 建立複製版本避免覆寫快取
        new_res = res.model_copy()
        new_res.results = filtered_results
        return new_res

aggregator = PriceAggregator()
