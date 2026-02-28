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
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    session = requests.Session()
    
    try:
        # 1. 取得 formhash
        res = session.get('https://apk.tw', headers=headers)
        formhash_match = re.search(r'name="formhash" value="([^"]+)"', res.text)
        
        if not formhash_match:
            print("⚠️ 無法取得 formhash。可能是 Cookie 格式不正確或已失效。")
            return
        
        formhash = formhash_match.group(1)
        print(f"✅ 取得最新 formhash: {formhash}")

        # 2. 簽到 URL (直接使用完整 URL 字串)
        # APK.TW 的簽到路徑通常為以下格式
        sign_url = "https://apk.tw&operation=qiandao&infloat=1&inajax=1"
        
        data = {
            'formhash': formhash,
            'qmd': 'kx',
            'todaysay': 'GitHub Actions 自動簽到成功！'
        }
        
        # 3. 發送請求
        sign_res = session.post(sign_url, headers=headers, data=data)
        
        # 4. 判斷結果
        response_text = sign_res.text
        if "簽到成功" in response_text:
            print("🎉 【成功】恭喜！今日簽到已完成。")
        elif "今日已簽到" in response_text or "您隔天再來" in response_text or "您今天已經簽到過" in response_text:
            print("🟡 【重複】你今天已經簽到過了。")
        elif "需要先登入" in response_text:
            print("❌ 【失敗】Cookie 驗證失敗，請檢查 Secrets 是否包含 saltkey 與 auth。")
        else:
            # 擷取 CDATA 中的文字訊息
            msg = re.search(r'CDATA\[(.*?)\]', response_text)
            if msg:
                print(f"❓ 【訊息】: {msg.group(1)}")
            else:
                # 如果回傳的是 HTML，嘗試抓取 div 內的錯誤文字
                error_msg = re.search(r'<div class="f_c">([\s\S]*?)</div>', response_text)
                print(f"❓ 【狀態】: {error_msg.group(1).strip() if error_msg else '請檢查 Cookie 完整性'}")

    except Exception as e:
        print(f"🚀 執行過程發生錯誤: {e}")

if __name__ == "__main__":
    start_sign()
