import os
from pydantic import BaseModel

class Settings(BaseModel):
    PROJECT_NAME: str = "台灣電商比價網 (TW Price Hunter)"
    API_V1_STR: str = "/api/v1"
    CACHE_TTL_SECONDS: int = 900  # 15 分鐘快取
    REQUEST_TIMEOUT: float = 12.0  # 爬蟲連線超時秒數
    MAX_RESULTS_PER_PLATFORM: int = 30
    
    # 預設啟用的電商平台
    DEFAULT_ENABLED_PLATFORMS: list[str] = ["pchome", "momo", "yahoo", "ruten", "shopee"]

settings = Settings()
