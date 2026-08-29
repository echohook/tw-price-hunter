FROM python:3.11-slim

# 設定工作目錄
WORKDIR /app

# 避免 Python 生成 .pyc 檔案與啟用標準輸出無緩衝
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/backend

# 安裝依賴套件
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt

# 複製專案檔案
COPY backend/ /app/backend/
COPY frontend/ /app/frontend/

# 開放連接埠
EXPOSE 8000

# 啟動命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
