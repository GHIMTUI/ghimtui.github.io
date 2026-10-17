import re
import requests
from channels import CHANNELS

def check_link_alive(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        if response.status_code in [200, 301, 302]:
            return True
    except Exception as e:
        print(f"Lỗi kết nối: {url} | {e}")
    return False

def get_active_url(url_list):
    if isinstance(url_list, str):
        return url_list
    for idx, url in enumerate(url_list):
        print(f"Đang kiểm tra link {idx + 1}: {url}")
        if check_link_alive(url):
            print(f"-> Link {idx + 1} SỐNG. Đã chọn.")
            return url
        else:
            print(f"-> Link {idx + 1} CHẾT.")
    return url_list[0] if url_list else None

def update_m3u_file(m3u_path="tivi.m3u"):
    try:
        with open(m3u_path, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Không tìm thấy file {m3u_path}")
        return

    updated_count = 0
    for channel_key, data in CHANNELS.items():
        tvg_id = data["tvg_id"]
        url_list = data["url"]
        
        active_url = get_active_url(url_list)
        if not active_url:
            continue

        # Regex tìm #EXTINF chứa tvg-id, bỏ qua các dòng #EXTVLCOPT (nếu có), và bắt đúng dòng URL (http/https)
        pattern = re.compile(
            rf'(#EXTINF:[^\n]*?tvg-id=["\']?{re.escape(tvg_id)}["\']?[^\n]*\n(?:#EXTVLCOPT:[^\n]*\n)*)(https?://[^\n]+)',
            re.IGNORECASE
        )
        
        match = pattern.search(content)
        if match:
            content = pattern.sub(rf'\1{active_url}', content)
            print(f"Đã cập nhật thành công link cho: {tvg_id}")
            updated_count += 1
        else:
            print(f"Không tìm thấy tvg-id=\"{tvg_id}\" trong file m3u.")

    if updated_count > 0:
        with open(m3u_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("Đã lưu lại file tivi.m3u thành công.")
    else:
        print("Không có thay đổi nào được thực hiện.")

if __name__ == "__main__":
    update_m3u_file()
