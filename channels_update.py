import re
import requests
from channels import CHANNELS

def get_real_stream_link(url):
    """
    Hàm getlink vỏ bọc (kể cả loại ngụy trang đuôi .m3u8):
    Truy cập vào URL, phân tích nội dung bên trong để tìm ra link m3u8 / luồng phát thực sự.
    """
    print(f"Đang phân tích/getlink nguồn: {url}")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': url
        }
        response = requests.get(url, headers=headers, timeout=12, allow_redirects=True)
        
        # Nếu link chuyển hướng (redirect) đi nơi khác và tận cùng là stream thật
        if response.url and response.url != url and (".m3u8" in response.url or "live" in response.url):
            if not response.url.endswith("/index.m3u8") and not "vietanhtv.id.vn" in response.url:
                print(f" -> Lấy được link qua hướng chuyển hướng: {response.url}")
                return response.url

        if response.status_code == 200 and response.text:
            text_content = response.text
            
            # 1. Nếu bên trong nội dung trả về có chứa các dòng link .m3u8 khác (đặc trưng của file playlist phụ hoặc iframe/script chứa link thật)
            # Lọc bỏ chính nó nếu nó tự trỏ lại nó
            m3u8_matches = re.findall(r'(https?://[^\s<>"\']+?\.m3u8[^\s<>"\']*)', text_content)
            for found_link in m3u8_matches:
                # Loại bỏ trường hợp nó tự trỏ về chính link ngụy trang ban đầu
                if found_link != url:
                    print(f" -> Đã bóc tách thành công link m3u8 gốc từ bên trong: {found_link}")
                    return found_link
            
            # 2. Trường hợp nội dung là mã nguồn trang web chứa link stream ẩn trong script hoặc player
            stream_matches = re.findall(r'["\'](https?://[^"\']+\bstream\b[^"\']*|\bhttps?://[^"\']+\.ts[^"\']*)["\']', text_content, re.IGNORECASE)
            if stream_matches:
                print(f" -> Tìm thấy stream phụ: {stream_matches[0]}")
                return stream_matches[0]

    except Exception as e:
        print(f" Lỗi khi bóc tách link từ {url}: {e}")
        
    # Nếu không bóc tách được gì thêm hoặc bản thân nó chính là link m3u8 thật duy nhất dùng được
    print(f" -> Sử dụng trực tiếp link hiện tại.")
    return url

def check_link_alive(url):
    """Kiểm tra xem link thực tế có đang hoạt động không"""
    if not url:
        return False
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        # Chấp nhận các mã thành công hoặc phản hồi từ server streaming
        if response.status_code in [200, 301, 302]:
            return True
    except Exception as e:
        print(f" Kiểm tra sống chết lỗi: {url} | {e}")
    return False

def get_active_url(url_list):
    """Duyệt qua danh sách url: Getlink vỏ bọc/ngụy trang -> Lấy m3u8 thật -> Kiểm tra sống"""
    if isinstance(url_list, str):
        url_list = [url_list]
        
    for idx, raw_url in enumerate(url_list):
        print(f"\n--- Kiểm tra nguồn {idx + 1}: {raw_url}")
        
        # Bước 1: Bóc tách lớp ngụy trang để lấy link gốc
        real_url = get_real_stream_link(raw_url)
        
        # Bước 2: Kiểm tra link gốc xem có thực sự sống không
        if real_url and check_link_alive(real_url):
            print(f"-> Link gốc hợp lệ và SỐNG. Đã chọn!")
            return real_url
        else:
            print(f"-> Nguồn này không khả dụng hoặc link chết. Chuyển sang nguồn tiếp theo...")
            
    return None

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
            print(f"Cảnh báo: Không thể lấy được link cho kênh {tvg_id}.")
            continue

        # Regex tìm chính xác vị trí kênh trong tivi.m3u theo tvg-id
        pattern = re.compile(
            rf'(#EXTINF:[^\n]*?tvg-id=["\']?{re.escape(tvg_id)}["\']?[^\n]*\n(?:#EXTVLCOPT:[^\n]*\n)*)(https?://[^\n]+)',
            re.IGNORECASE
        )
        
        match = pattern.search(content)
        if match:
            content = pattern.sub(rf'\1{active_url}', content)
            print(f" Đã thay thế link gốc chuẩn vào tivi.m3u cho ID: {tvg_id}\n")
            updated_count += 1
        else:
            print(f"Không tìm thấy tvg-id=\"{tvg_id}\" trong file tivi.m3u.\n")

    if updated_count > 0:
        with open(m3u_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("HOÀN TẤT! Đã lưu file tivi.m3u thành công.")
    else:
        print("Không có thay đổi nào được ghi.")

if __name__ == "__main__":
    update_m3u_file()
