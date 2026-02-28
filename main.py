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
        'X-Requested-With': 'XMLHttpRequest'
    }

    session = requests.Session()
    
    try:
        # 1. 取得 formhash
        res = session.get('https://apk.tw', headers=headers)
        formhash_match = re.search(r'name="formhash" value="([^"]+)"', res.text)
        
        if not formhash_match:
            print("⚠️ 無法取得 formhash。請檢查 Cookie 內容，必須包含 _saltkey 與 _auth。")
            return
        
        formhash = formhash_match.group(1)
        print(f"✅ 取得最新 formhash: {formhash}")

        # 2. 修正網址拼接：將參數與 URL 分離
        # 這樣 requests 會自動幫你組合出正確的 https://apk.tw...
        target_url = "https://apk.tw"
        query_params = {
            'id': 'dsu_paulsign:sign',
            'operation': 'qiandao',
            'infloat': '1',
            'inajax': '1'
        }
        post_data = {
            'formhash': formhash,
            'qmd': 'kx',
            'todaysay': 'GitHub Actions 自動簽到成功！'
        }
        
        # 關鍵：params 用於網址參數，data 用於表單內容
        sign_res = session.post(target_url, headers=headers, params=query_params, data=post_data)
        
        # 3. 判斷結果
        response_text = sign_res.text
        if "簽到成功" in response_text:
            print("🎉 【成功】恭喜！今日簽到已完成。")
        elif any(msg in response_text for msg in ["今日已簽到", "您隔天再來", "您今天已經簽到過"]):
            print("🟡 【重複】你今天已經簽到過了，無需操作。")
        elif "需要先登入" in response_text:
            print("❌ 【失敗】Cookie 已失效，請重新抓取。")
        else:
            # 抓取 XML 或 HTML 中的訊息內容
            msg = re.search(r'CDATA\[(.*?)\]', response_text)
            if not msg:
                msg = re.search(r'<div class="f_c">([\s\S]*?)</div>', response_text)
            
            result_text = msg.group(1).strip() if msg else "未知回傳內容"
            print(f"❓ 【訊息】: {result_text}")

    except Exception as e:
        print(f"🚀 執行過程發生錯誤: {e}")

if __name__ == "__main__":
    start_sign()
