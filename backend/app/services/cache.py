import time
from typing import Optional, Dict, Any
from app.models.product import SearchResponse
from app.config import settings

class SearchCache:
    """記憶體搜尋結果快取服務 (支援 TTL 過期機制)"""
    
    def __init__(self, default_ttl: int = settings.CACHE_TTL_SECONDS):
        self.default_ttl = default_ttl
        self._cache: Dict[str, Dict[str, Any]] = {}

    def _make_key(self, keyword: str, platforms: list[str]) -> str:
        sorted_platforms = "_".join(sorted(platforms))
        return f"{keyword.strip().lower()}:{sorted_platforms}"

    def get(self, keyword: str, platforms: list[str]) -> Optional[SearchResponse]:
        key = self._make_key(keyword, platforms)
        item = self._cache.get(key)
        if not item:
            return None
        
        # 檢查是否已過期
        if time.time() > item["expires_at"]:
            del self._cache[key]
            return None
        
        cached_response: SearchResponse = item["data"]
        # 標記為快取資料
        cached_response.cached = True
        return cached_response

    def set(self, keyword: str, platforms: list[str], data: SearchResponse, ttl: Optional[int] = None):
        key = self._make_key(keyword, platforms)
        duration = ttl or self.default_ttl
        self._cache[key] = {
            "data": data,
            "expires_at": time.time() + duration
        }

    def clear(self):
        self._cache.clear()

search_cache = SearchCache()
