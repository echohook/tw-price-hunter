import pytest
import asyncio
from app.crawlers.pchome import PChomeCrawler
from app.crawlers.momo import MomoCrawler
from app.crawlers.yahoo import YahooCrawler
from app.crawlers.shopee import ShopeeCrawler
from app.crawlers.mock import MockCrawler

@pytest.mark.asyncio
async def test_mock_crawler():
    crawler = MockCrawler()
    items, elapsed, err = await crawler.search("衛生紙", limit=5)
    assert err is None
    assert len(items) == 5
    assert items[0].price > 0
    assert items[0].platform == "測試商城 (Mock)"
    assert items[0].product_url.startswith("http")

@pytest.mark.asyncio
async def test_pchome_crawler():
    crawler = PChomeCrawler()
    items, elapsed, err = await crawler.search("PS5", limit=5)
    assert err is None
    assert len(items) > 0
    assert items[0].platform_id == "pchome"
    assert items[0].price > 0
    assert "24h.pchome.com.tw" in items[0].product_url

@pytest.mark.asyncio
async def test_momo_crawler():
    crawler = MomoCrawler()
    items, elapsed, err = await crawler.search("PS5", limit=5)
    assert err is None
    assert len(items) > 0
    assert items[0].platform_id == "momo"
    assert items[0].price > 0
    assert "momoshop.com.tw" in items[0].product_url

@pytest.mark.asyncio
async def test_yahoo_crawler():
    crawler = YahooCrawler()
    items, elapsed, err = await crawler.search("PS5", limit=5)
    assert err is None
    assert len(items) > 0
    assert items[0].platform_id == "yahoo"
    assert items[0].price > 0
    assert "buy.yahoo.com" in items[0].product_url

@pytest.mark.asyncio
async def test_shopee_crawler():
    crawler = ShopeeCrawler()
    items, elapsed, err = await crawler.search("PS5", limit=5)
    assert err is None
    assert len(items) > 0
    assert items[0].platform_id == "shopee"
