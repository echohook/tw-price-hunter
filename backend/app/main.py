import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse

from app.config import settings
from app.api.v1.search import router as search_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="台灣主流綜合電商 (PChome, Momo, Yahoo, 露天拍賣, 蝦皮) 即時跨平台比價搜尋引擎",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs"
)

# 設定 CORS 跨域請求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 註冊 API 路由
app.include_router(search_router, prefix=settings.API_V1_STR, tags=["Search & Compare"])

# 定位前端靜態檔案目錄 (tw_price_hunter/frontend/static)
current_dir = os.path.dirname(os.path.abspath(__file__))
possible_static_paths = [
    os.path.abspath(os.path.join(current_dir, "../../frontend/static")),
    os.path.abspath(os.path.join(current_dir, "../../../frontend/static")),
    os.path.abspath(os.path.join(os.getcwd(), "frontend/static")),
    os.path.abspath(os.path.join(os.getcwd(), "../frontend/static")),
]

frontend_static_dir = None
for p in possible_static_paths:
    if os.path.exists(p):
        frontend_static_dir = p
        break

if frontend_static_dir and os.path.exists(frontend_static_dir):
    app.mount("/static", StaticFiles(directory=frontend_static_dir), name="static")

    @app.get("/", response_class=FileResponse, include_in_schema=False)
    async def serve_index():
        index_file = os.path.join(frontend_static_dir, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return HTMLResponse("<h1>Index file not found</h1>", status_code=404)
else:
    @app.get("/", include_in_schema=False)
    async def serve_fallback():
        return {
            "message": "TW Price Hunter API is running. Static files path not located.",
            "searched_paths": possible_static_paths
        }

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "app": settings.PROJECT_NAME, "version": "1.0.0"}
