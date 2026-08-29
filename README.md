# 台灣電商即時比價網 (TW Price Hunter)

台灣主流綜合電商（PChome 24h、Momo 購物網、Yahoo 購物中心、蝦皮購物）即時非同步跨平台商品比價搜尋引擎。

## 🌟 核心特色
- **非同步並行爬蟲**：多平台同時搜尋，1.3 秒取得跨平台完整報價。
- **智慧商品聚合**：自動過濾標題促銷贅詞，跨平台歸類同款商品並計算價差。
- **全網最低價標記**：自動高亮全網最低價與推薦購買平台。
- **外掛式適配器架構**：繼承 `BaseCrawler` 即可無痛擴充新電商。
- **現代化響應式 UI**：支援雙檢視模式（聚合比價 / 全商品清單）、即時排序與電商篩選。

## 🚀 快速開始 (本地運行)

1. 安裝相依套件：
```bash
pip install -r backend/requirements.txt
```

2. 啟動伺服器：
```bash
python backend/run.py
```
開啟瀏覽器訪問: `http://localhost:8000`

## ☁️ 雲端 PaaS 部署 (Zeabur / Render)
專案內建 `Dockerfile` 與 `Procfile`，直接連接 GitHub 倉庫即可一鍵完成部署。
- **Build Command**: `pip install -r backend/requirements.txt`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT --app-dir backend`
