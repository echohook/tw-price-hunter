import pytest
from app.services.aggregator import aggregator
from app.services.matcher import ProductMatcher
from app.models.product import ProductItem

@pytest.mark.asyncio
async def test_aggregator_search():
    # 測試多平台非同步並行比價
    res = await aggregator.search("PS5 Slim", platforms=["pchome", "yahoo", "mock"], use_cache=False)
    assert res.total_found > 0
    assert res.lowest_price > 0
    assert res.highest_price >= res.lowest_price
    assert len(res.platforms_status) == 3
    assert len(res.results) > 0
    # 檢查最低價標籤
    lowest_items = [it for it in res.results if it.is_lowest_price]
    assert len(lowest_items) > 0
    assert lowest_items[0].price == res.lowest_price

def test_product_matcher():
    cleaned = ProductMatcher.clean_title("【SONY 官方旗艦】PlayStation 5 Slim 1TB 主機 (24h現貨特惠免運)")
    assert "PlayStation 5 Slim 1TB" in cleaned
    assert "【SONY" not in cleaned
    assert "24h現貨特惠免運" not in cleaned

    sim = ProductMatcher.calculate_similarity(
        "SONY PS5 Slim 1TB 光碟版",
        "【狂降】PS5 Slim 1TB 光碟版主機 現貨"
    )
    assert sim > 0.4
