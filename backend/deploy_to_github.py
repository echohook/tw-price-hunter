import os
import sys
import httpx
import base64
import json

# 確保 Windows 控制台輸出正常
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def get_all_files():
    """收集專案內需要上傳的檔案"""
    ignore_dirs = {".git", ".pytest_cache", "__pycache__", "venv", "env", ".venv", ".agents"}
    ignore_extensions = {".pyc", ".pyo", ".pyd"}
    
    file_list = []
    for root, dirs, files in os.walk(PROJECT_ROOT):
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        for f in files:
            ext = os.path.splitext(f)[1]
            if ext in ignore_extensions:
                continue
            full_path = os.path.join(root, f)
            rel_path = os.path.relpath(full_path, PROJECT_ROOT).replace("\\", "/")
            file_list.append((rel_path, full_path))
    return file_list

def deploy_to_github(github_token: str, repo_name: str = "tw-price-hunter", is_private: bool = False):
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "TW-Price-Hunter-Deployer"
    }

    with httpx.Client(timeout=30.0, headers=headers) as client:
        # 1. 取得使用者資訊
        user_res = client.get("https://api.github.com/user")
        if user_res.status_code != 200:
            print(f"[!] GitHub 驗證失敗: {user_res.status_code} - {user_res.text}")
            return False
        
        username = user_res.json().get("login")
        print(f"[*] 成功登入 GitHub 帳號: @{username}")

        # 2. 建立新倉庫
        create_payload = {
            "name": repo_name,
            "description": "台灣主流電商 (PChome, Momo, Yahoo, 蝦皮) 即時比價網站",
            "private": is_private,
            "auto_init": False
        }
        repo_res = client.post("https://api.github.com/user/repos", json=create_payload)
        if repo_res.status_code == 201:
            print(f"[*] 成功建立新倉庫: {username}/{repo_name}")
        elif repo_res.status_code == 422:
            print(f"[*] 倉庫 {username}/{repo_name} 已存在，將直接更新檔案...")
        else:
            print(f"[!] 建立倉庫失敗: {repo_res.status_code} - {repo_res.text}")
            return False

        # 3. 逐一上傳檔案
        files = get_all_files()
        print(f"[*] 準備上傳 {len(files)} 個專案檔案至 GitHub...")

        for rel_path, full_path in files:
            with open(full_path, "rb") as f:
                content_bytes = f.read()
            b64_content = base64.b64encode(content_bytes).decode("utf-8")

            # 檢查檔案是否已存在以取得 sha
            check_url = f"https://api.github.com/repos/{username}/{repo_name}/contents/{rel_path}"
            check_res = client.get(check_url)
            sha = check_res.json().get("sha") if check_res.status_code == 200 else None

            put_payload = {
                "message": f"Add {rel_path}",
                "content": b64_content
            }
            if sha:
                put_payload["sha"] = sha

            put_res = client.put(check_url, json=put_payload)
            if put_res.status_code in (200, 201):
                print(f"  -> 已成功上傳: {rel_path}")
            else:
                print(f"  -> 上傳失敗 {rel_path}: {put_res.status_code} {put_res.text[:100]}")

        repo_url = f"https://github.com/{username}/{repo_name}"
        print("=" * 60)
        print(f"[SUCCESS] 專案已成功自動推送至 GitHub: {repo_url}")
        print("=" * 60)
        return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方式: python backend/deploy_to_github.py <GITHUB_PERSONAL_ACCESS_TOKEN>")
        sys.exit(1)
    deploy_to_github(sys.argv[1])
