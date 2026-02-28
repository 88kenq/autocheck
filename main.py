import os
import requests
import re

# 從 GitHub Secrets 讀取 Cookie
COOKIE = os.environ.get('APK_COOKIE')

def start_sign():
    if not COOKIE:
        print("❌ 錯誤：找不到 APK_COOKIE 設定")
        return

    # 完整模擬瀏覽器標頭
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Cookie': COOKIE,
        'Referer': 'https://apk.tw',
        'Origin': 'https://apk.tw',
        'Accept': 'application/xml, text/xml, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest'
    }

    session = requests.Session()
    
    try:
        # 1. 取得 formhash
        res = session.get('https://apk.tw', headers=headers)
        formhash_match = re.search(r'name="formhash" value="([^"]+)"', res.text)
        
        if not formhash_match:
            print("⚠️ 無法取得 formhash。可能是 Cookie 不完整（需包含 saltkey 與 auth）。")
            return
        
        formhash = formhash_match.group(1)
        print(f"✅ 取得最新 formhash: {formhash}")

        # 2. 準備簽到參數與資料
        sign_url = "https://apk.tw&operation=qiandao&infloat=1&inajax=1"
        data = {
            'formhash': formhash,
            'qmd': 'kx',
            'todaysay': 'GitHub Actions 自動簽到成功！',
            'fastpostrefresh': '1'
        }
        
        # 3. 發送請求
        sign_res = session.post(sign_url, headers=headers, data=data)
        
        # 4. 精確判斷回傳內容
        response_text = sign_res.text
        
        # 檢查是否成功或重複
        if "簽到成功" in response_text:
            print("🎉 【成功】恭喜！今日簽到已完成。")
        elif any(msg in response_text for msg in ["今日已簽到", "您隔天再來", "您今天已經簽到過"]):
            print("🟡 【重複】你今天已經簽到過了。")
        elif "需要先登入" in response_text:
            print("❌ 【失敗】Cookie 驗證失敗，請檢查 Secrets。")
        else:
            # 如果是 XML 格式，嘗試提取 CDATA
            cdata = re.search(r'CDATA\[(.*?)\]', response_text)
            if cdata:
                print(f"❓ 【回傳訊息】: {cdata.group(1)}")
            else:
                # 顯示前 150 字方便你複製給我看
                print(f"❓ 【回傳 HTML 預覽】: {response_text[:150].strip()}")

    except Exception as e:
        print(f"🚀 執行過程發生錯誤: {e}")

if __name__ == "__main__":
    start_sign()

    start_sign()
