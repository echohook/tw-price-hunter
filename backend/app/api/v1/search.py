from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from app.models.product import SearchResponse
from app.services.aggregator import aggregator

router = APIRouter()

@router.get("/search", response_model=SearchResponse, summary="跨平台商品比價搜尋")
async def search_products(
    q: str = Query(..., description="搜尋關鍵字 (例如: iPhone 16, PS5, 衛生紙)", min_length=1),
    platforms: Optional[str] = Query(None, description="指定比價平台 (逗號分隔，例如: pchome,momo,yahoo,shopee)"),
    sort: str = Query("price_asc", description="排序方式: price_asc (價格低到高), price_desc (價格高到低), platform (依平台)"),
    min_price: Optional[float] = Query(None, description="最低價格過濾"),
    max_price: Optional[float] = Query(None, description="最高價格過濾"),
    no_cache: bool = Query(False, description="是否略過快取直接向電商抓取最新價格")
):
    platform_list = [p.strip().lower() for p in platforms.split(",")] if platforms else None
    
    try:
        response = await aggregator.search(
            keyword=q,
            platforms=platform_list,
            sort_by=sort,
            min_price=min_price,
            max_price=max_price,
            use_cache=not no_cache
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"比價搜尋處理失敗: {str(e)}")

@router.get("/platforms", summary="取得所有支援的比價電商清單")
async def get_platforms():
    return {
        "status": "success",
        "platforms": aggregator.get_supported_platforms()
    }

@router.get("/trending", summary="熱門搜尋比價關鍵字")
async def get_trending_keywords():
    return {
        "trending": [
            {"keyword": "PS5 Slim", "category": "電玩遊戲", "tag": "超人氣"},
            {"keyword": "iPhone 16", "category": "3C 旗艦", "tag": "熱搜"},
            {"keyword": "Switch OLED", "category": "電玩遊戲", "tag": "熱賣"},
            {"keyword": "舒潔 衛生紙", "category": "生活日用", "tag": "箱購省"},
            {"keyword": "Dyson 吹風機", "category": "美髮家電", "tag": "狂降"},
            {"keyword": "國際牌 除濕機", "category": "季節家電", "tag": "推薦"},
            {"keyword": "RTX 4070", "category": "電腦硬體", "tag": "特惠"},
            {"keyword": "AirPods Pro 2", "category": "音訊耳機", "tag": "熱搜"}
        ]
    }
