import os
import sys

# 確保 Windows 控制台使用 UTF-8 編碼
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# 將 backend 目錄加入 sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import uvicorn

if __name__ == "__main__":
    print("=" * 65)
    print("[*] 正在啟動 台灣電商比價網 (TW Price Hunter) 伺服器...")
    print("[*] 網站首頁: http://localhost:8000")
    print("[*] API 文件: http://localhost:8000/docs")
    print("=" * 65)
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False
    )
