from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ProductItem(BaseModel):
    """統一跨平台商品資料模型"""
    id: str = Field(..., description="商品唯一識別碼 (含平台前綴)")
    title: str = Field(..., description="商品標題/名稱")
    price: float = Field(..., description="當前售價 (新台幣 NT$)")
    original_price: Optional[float] = Field(None, description="原價/建議售價")
    platform: str = Field(..., description="平台名稱 (如 PChome 24h, Momo 購物網, Yahoo 購物, 蝦皮購物)")
    platform_id: str = Field(..., description="平台識別碼 (pchome, momo, yahoo, shopee)")
    platform_badge_color: str = Field(default="blue", description="前端平台標籤色調")
    product_url: str = Field(..., description="商品原始購買網址")
    image_url: str = Field(..., description="商品主要圖片網址")
    in_stock: bool = Field(default=True, description="是否有現貨/可購買")
    rating: Optional[float] = Field(None, description="評分 (0.0 ~ 5.0)")
    rating_count: Optional[int] = Field(None, description="評論數")
    tags: List[str] = Field(default_factory=list, description="促銷或特色標籤 (例如 24h到貨、折價券、免運)")
    shipping_info: Optional[str] = Field(None, description="運費或配送說明")
    is_lowest_price: bool = Field(default=False, description="是否為全網最低價")
    price_diff_with_lowest: float = Field(default=0.0, description="與全網最低價之差額")


class ComparisonGroup(BaseModel):
    """同款/相似商品比價群組"""
    group_id: str = Field(..., description="群組唯一識別碼")
    normalized_title: str = Field(..., description="正規化標準商品名稱")
    lowest_price: float = Field(..., description="該款商品跨平台最低價")
    highest_price: float = Field(..., description="該款商品跨平台最高價")
    price_diff: float = Field(..., description="最高與最低價差")
    price_diff_percent: float = Field(..., description="價差百分比 (0~100%)")
    best_deal_item: ProductItem = Field(..., description="最划算商品項目")
    items: List[ProductItem] = Field(..., description="同款商品在各家電商的列表")
    platforms_available: List[str] = Field(..., description="有販售該商品的平台清單")


class PlatformStatus(BaseModel):
    platform_id: str
    platform_name: str
    is_active: bool
    response_time_ms: float
    items_count: int
    error: Optional[str] = None


class SearchResponse(BaseModel):
    """搜尋比價結果綜合回應"""
    keyword: str = Field(..., description="搜尋關鍵字")
    total_found: int = Field(..., description="抓取到的商品總數")
    lowest_price: float = Field(default=0.0, description="全網最低價")
    average_price: float = Field(default=0.0, description="全網平均價")
    highest_price: float = Field(default=0.0, description="全網最高價")
    platforms_searched: List[str] = Field(default_factory=list, description="參與比價的平台名稱清單")
    platforms_status: List[PlatformStatus] = Field(default_factory=list, description="各平台抓取狀態與效能")
    results: List[ProductItem] = Field(default_factory=list, description="商品清單 (已排序)")
    comparison_groups: List[ComparisonGroup] = Field(default_factory=list, description="同款商品聚合比價群組")
    execution_time_ms: float = Field(..., description="總執行時間 (毫秒)")
    cached: bool = Field(default=False, description="是否來自快取")
