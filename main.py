import os
import requests
import re
from urllib.parse import quote

# 從 GitHub Secrets 讀取 Cookie
COOKIE = os.environ.get('APK_COOKIE')

def start_sign():
    if not COOKIE:
        print("❌ 錯誤：找不到 APK_COOKIE 設定")
        return

    # 模擬真實瀏覽器的 Headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Cookie': COOKIE,
        'Referer': 'https://apk.tw',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'Origin': 'https://apk.tw',
        'Upgrade-Insecure-Requests': '1'
    }

    session = requests.Session()
    
    try:
        # 1. 先訪問簽到主頁面，建立 session 狀態
        res = session.get('https://apk.tw', headers=headers)
        formhash_match = re.search(r'name="formhash" value="([^"]+)"', res.text)
        
        if not formhash_match:
            print("⚠️ 無法取得 formhash，請檢查 Cookie 是否貼對（需包含 _saltkey 與 _auth）")
            return
        
        formhash = formhash_match.group(1)
        print(f"✅ 取得最新 formhash: {formhash}")

        # 2. 準備簽到數據 (APK.TW 有時需要 qmd 與 todaysay)
        # 注意：使用 data 而非 params 模擬 POST 表單提交
        data = {
            'formhash': formhash,
            'qmd': 'kx',  # 選擇：開心
            'todaysay': 'GitHub Actions 自動簽到成功！',
            'fastpostrefresh': '1'
        }
        
        # 關鍵：簽到 URL 必須完整，並模擬 Ajax 請求
        sign_url = "https://apk.tw&operation=qiandao&infloat=1&inajax=1"
        
        sign_res = session.post(sign_url, headers=headers, data=data)
        
        # 3. 解析回傳內容 (處理 XML 格式回傳)
        response_text = sign_res.text
        
        if "簽到成功" in response_text:
            print("🎉 【成功】恭喜！今日簽到已完成。")
        elif "今日已簽到" in response_text or "您隔天再來" in response_text or "您今天已經簽到過了" in response_text:
            print("🟡 【重複】你今天已經簽到過了，無需重複操作。")
        elif "需要先登入" in response_text:
            print("❌ 【失敗】Cookie 已失效，請從瀏覽器重新抓取並更新 Secrets。")
        else:
            # 如果還是失敗，顯示關鍵字以便除錯
            if "CDATA" in response_text:
                # 擷取 XML CDATA 內部的文字
                clean_text = re.search(r'CDATA\[(.*?)\]', response_text)
                print(f"❓ 【回傳訊息】: {clean_text.group(1) if clean_text else response_text[:50]}")
            else:
                print(f"❓ 【未知狀態】: {response_text[:100]}")

    except Exception as e:
        print(f"🚀 執行過程發生錯誤: {e}")

if __name__ == "__main__":
    start_sign()
