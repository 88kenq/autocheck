import os
import requests
import re

# 從 GitHub Secrets 讀取 Cookie
COOKIE = os.environ.get("APKTW_COOKIE")

def check_in():
    url = "https://apk.tw"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Cookie": COOKIE,
        "Referer": "https://apk.tw"
    }
    
    # 1. 獲取 Formhash (Discuz 系統必備驗證碼)
    res = requests.get("https://apk.tw", headers=headers)
    formhash = re.search(r'formhash=(\w+)', res.text)
    
    if not formhash:
        print("錯誤：無法獲取 formhash，請檢查 Cookie 是否失效。")
        return

    # 2. 執行簽到 (qmd=kx 代表心情為「開心」)
    payload = {
        "formhash": formhash.group(1),
        "qmd": "kx", 
        "todaysay": "GitHub Actions 自動簽到",
        "fastpost": "0"
    }
    
    response = requests.post(url, headers=headers, data=payload)
    if "簽到成功" in response.text or "已經簽到" in response.text:
        print("簽到成功或今日已簽到！")
    else:
        print("簽到失敗，回應內容：", response.text[:200])

if __name__ == "__main__":
    check_in()
