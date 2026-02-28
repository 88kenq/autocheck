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
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Cookie': COOKIE,
        'Referer': 'https://apk.tw'
    }

    session = requests.Session()
    
    try:
        # 1. 先訪問簽到頁面抓取 formhash
        res = session.get('https://apk.tw', headers=headers)
        formhash_match = re.search(r'name="formhash" value="([^"]+)"', res.text)
        
        if not formhash_match:
            print("⚠️ 無法取得 formhash，請檢查 Cookie 是否正確貼上")
            return
        
        formhash = formhash_match.group(1)
        print(f"✅ 取得 formhash: {formhash}")

        # 2. 修正後的簽到網址與參數
        sign_url = "https://apk.tw"
        params = {
            'id': 'dsu_paulsign:sign',
            'operation': 'qiandao',
            'infloat': '1',
            'inajax': '1'
        }
        data = {
            'formhash': formhash,
            'qmd': 'kx',  # 心情：開心
            'todaysay': '自動簽到成功！'
        }
        
        # 使用 params 帶入參數，避免網址解析錯誤
        sign_res = session.post(sign_url, headers=headers, params=params, data=data)
        
        # 3. 判斷結果
        if "簽到成功" in sign_res.text:
            print("🎉 【成功】恭喜！今日簽到已完成。")
        elif "今日已簽到" in sign_res.text or "您隔天再來" in sign_res.text:
            print("🟡 【重複】你今天已經簽到過了。")
        elif "需要先登入" in sign_res.text:
            print("❌ 【失敗】Cookie 已失效，請重新抓取。")
        else:
            print("❓ 【結果】" + sign_res.text[:100])

    except Exception as e:
        print(f"🚀 執行過程發生錯誤: {e}")

if __name__ == "__main__":
    start_sign()
