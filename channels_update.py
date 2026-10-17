import re
import requests
from channels import CHANNELS

def get_real_stream_link(url):
    """
    Hàm getlink vỏ bọc: Trích xuất hoặc giải mã để lấy link m3u8 thực tế.
    Tùy thuộc vào từng dạng link vỏ bọc của bạn, có thể bổ sung logic xử lý ở đây.
    """
    print(f"Đang getlink vỏ bọc cho: {url}")
    
    # Nếu bản thân link đã là .m3u8 thì giữ nguyên
    if url.endswith(".m3u8") or ".m3u8?" in url:
        return url
        
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        
        # Ví dụ: Nếu trang vỏ bọc trả về nội dung chứa một link m3u8 bên trong văn bản hoặc redirect
        if response.status_code == 200:
            # Tìm kiếm định dạng m3u8 xuất hiện trong nội dung trang web vỏ bọc
            m3u8_matches = re.findall(r'(https?://[^\s<>"]+?\.m3u8[^\s<>"]*)', response.text)
            if m3u8_matches:
                real_link = m3u8_matches[0]
                print(f" -> Đã get thành công link m3u8 gốc: {real_link}")
                return real_link
                
        # Nếu không tìm thấy m3u8 bên trong nội dung nhưng URL cuối cùng sau redirect là m3u8
        if response.url.endswith(".m3u8"):
            return response.url
            
    except Exception as e:
        print(f" Lỗi khi getlink từ {url}: {e}")
        
    # Nếu không get được gì, trả về chính link gốc để fallback
    return url

def check_link_alive(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        if response.status_code in [200, 301, 302]:
            return True
    except Exception as e:
        print(f"Lỗi kết nối link gốc: {url} | {e}")
    return False

def get_active_url(url_list):
    if isinstance(url_list, str):
        url_list = [url_list]
        
    for idx, raw_url in enumerate(url_list):
        print(f"\n--- Kiểm tra nguồn {idx + 1}: {raw_url}")
        
        # BƯỚC 1: Get link vỏ bọc để lấy link m3u8 thực tế
        real_url = get_real_stream_link(raw_url)
        
        # BƯỚC 2: Kiểm tra xem link m3u8 thực tế đó có sống hay không
        if check_link_alive(real_url):
            print(f"-> Link m3u8 thực tế SỐNG. Đã chọn: {real_url}")
            return real_url
        else:
            print(f"-> Link m3u8 thực tế CHẾT. Đang chuyển nguồn tiếp theo...")
            
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
        
        # Thực hiện getlink và chọn link sống
        active_url = get_active_url(url_list)
        if not active_url:
            continue

        # Regex tìm đúng vị trí kênh dựa vào tvg-id và thay thế link m3u8 vào
        pattern = re.compile(
            rf'(#EXTINF:[^\n]*?tvg-id=["\']?{re.escape(tvg_id)}["\']?[^\n]*\n(?:#EXTVLCOPT:[^\n]*\n)*)(https?://[^\n]+)',
            re.IGNORECASE
        )
        
        match = pattern.search(content)
        if match:
            content = pattern.sub(rf'\1{active_url}', content)
            print(f"Đã cập nhật link m3u8 gốc vào tivi.m3u cho ID: {tvg_id}")
            updated_count += 1
        else:
            print(f"Không tìm thấy tvg-id=\"{tvg_id}\" trong file m3u.")

    if updated_count > 0:
        with open(m3u_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("\nĐÃ GHI VÀ LƯU THÀNH CÔNG VÀO FILE tivi.m3u!")
    else:
        print("\nKhông có thay đổi nào được ghi.")

if __name__ == "__main__":
    update_m3u_file()
