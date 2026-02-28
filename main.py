import os
import requests
import re

# 從 GitHub Secrets 讀取 Cookie
COOKIE = os.environ.get('APK_COOKIE')

def start_sign():
    if not COOKIE:
        print("❌ 錯誤：找不到 APK_COOKIE 設定")
        return

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Cookie': COOKIE,
        'Referer': 'https://apk.tw',
        'Origin': 'https://apk.tw',
        'X-Requested-With': 'XMLHttpRequest'
    }

    session = requests.Session()
    
    try:
        # 1. 取得 formhash
        res = session.get('https://apk.tw', headers=headers)
        formhash_match = re.search(r'name="formhash" value="([^"]+)"', res.text)
        
        if not formhash_match:
            print("⚠️ 無法取得 formhash，請檢查 Cookie 是否正確")
            return
        
        formhash = formhash_match.group(1)
        print(f"✅ 取得最新 formhash: {formhash}")

        # 2. 正確的網址與參數分離 (避免解析錯誤)
        url = "https://apk.tw"
        params = {
            'id': 'dsu_paulsign:sign',
            'operation': 'qiandao',
            'infloat': '1',
            'inajax': '1'
        }
        data = {
            'formhash': formhash,
            'qmd': 'kx',
            'todaysay': 'GitHub Actions 自動簽到成功！',
            'fastpostrefresh': '1'
        }
        
        # 使用 params 帶入 URL 參數，使用 data 帶入 POST 表單
        sign_res = session.post(url, headers=headers, params=params, data=data)
        
        # 3. 判斷結果
        response_text = sign_res.text
        if "簽到成功" in response_text:
            print("🎉 【成功】恭喜！今日簽到已完成。")
        elif "今日已簽到" in response_text or "您隔天再來" in response_text or "您今天已經簽到過了" in response_text:
            print("🟡 【重複】你今天已經簽到過了。")
        elif "需要先登入" in response_text:
            print("❌ 【失敗】Cookie 已失效，請重新抓取。")
        else:
            # 嘗試抓取 XML 中的錯誤訊息
            msg = re.search(r'CDATA\[(.*?)\]', response_text)
            print(f"❓ 【回傳訊息】: {msg.group(1) if msg else response_text[:50]}")

    except Exception as e:
        print(f"🚀 執行過程發生錯誤: {e}")

if __name__ == "__main__":
    start_sign()
