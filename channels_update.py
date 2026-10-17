import re
import requests
from channels import CHANNELS

def get_real_stream_link(url):
    """
    Hàm getlink vỏ bọc: Truy cập vào trang vỏ bọc (như vieon.php?id=...) 
    để trích xuất ra link .m3u8 thực tế bên trong.
    """
    print(f"Đang getlink từ nguồn: {url}")
    
    # Nếu bản thân link đã là .m3u8 trực tiếp thì trả về luôn
    if url.endswith(".m3u8") or ".m3u8?" in url:
        print(f" -> Đã là link .m3u8 trực tiếp.")
        return url
        
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': url
        }
        # Gửi request vào trang vỏ bọc
        response = requests.get(url, headers=headers, timeout=12, allow_redirects=True)
        
        # 1. Kiểm tra nếu ngay cả URL sau khi redirect (chuyển hướng) đã là .m3u8
        if response.url and (".m3u8" in response.url):
            print(f" -> Lấy được link .m3u8 từ URL chuyển hướng: {response.url}")
            return response.url
            
        # 2. Nếu trang trả về nội dung (HTML/JSON/Text), tiến hành dùng Regex quét tìm link .m3u8
        if response.status_code == 200 and response.text:
            # Tìm tất cả các định dạng chứa .m3u8 trong source hoặc nội dung trả về
            m3u8_matches = re.findall(r'(https?://[^\s<>"\']+?\.m3u8[^\s<>"\']*)', response.text)
            if m3u8_matches:
                real_link = m3u8_matches[0]
                print(f" -> Đã bóc tách thành công link .m3u8 gốc: {real_link}")
                return real_link
                
    except Exception as e:
        print(f" Lỗi khi getlink từ {url}: {e}")
        
    # Nếu không get được gì hoặc lỗi, trả về None để hệ thống biết đường chuyển qua link dự phòng (link2)
    print(f" -> Không thể get được link .m3u8 từ nguồn này.")
    return None

def check_link_alive(url):
    """Kiểm tra xem link .m3u8 thực tế có đang sống không"""
    if not url:
        return False
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        if response.status_code in [200, 301, 302]:
            return True
    except Exception as e:
        print(f" Kiểm tra link sống chết lỗi: {url} | {e}")
    return False

def get_active_url(url_list):
    """Duyệt qua danh sách url: Getlink vỏ bọc -> Lấy m3u8 -> Kiểm tra sống -> Trả về link ngon nhất"""
    if isinstance(url_list, str):
        url_list = [url_list]
        
    for idx, raw_url in enumerate(url_list):
        print(f"\n--- Thử nguồn số {idx + 1}: {raw_url}")
        
        # Bước 1: Gọi hàm getlink vỏ bọc để trích xuất ra .m3u8 thật
        real_url = get_real_stream_link(raw_url)
        
        # Bước 2: Kiểm tra xem link .m3u8 thật đó có hoạt động (sống) hay không
        if real_url and check_link_alive(real_url):
            print(f"-> Link .m3u8 thực tế SỐNG. Đã chọn đưa vào file tivi!")
            return real_url
        else:
            print(f"-> Nguồn này thất bại (hoặc link chết). Đang chuyển sang nguồn tiếp theo...")
            
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
        
        # Lấy link .m3u8 thực sự sau khi qua bộ lọc getlink & check sống
        active_url = get_active_url(url_list)
        if not active_url:
            print(f"Cảnh báo: Không thể lấy được link hoạt động cho kênh {tvg_id}. Giữ nguyên link cũ.")
            continue

        # Regex tìm đúng vị trí dòng link của kênh trong tivi.m3u dựa theo tvg-id
        pattern = re.compile(
            rf'(#EXTINF:[^\n]*?tvg-id=["\']?{re.escape(tvg_id)}["\']?[^\n]*\n(?:#EXTVLCOPT:[^\n]*\n)*)(https?://[^\n]+)',
            re.IGNORECASE
        )
        
        match = pattern.search(content)
        if match:
            content = pattern.sub(rf'\1{active_url}', content)
            print(f" Đã thay thế thành công link .m3u8 gốc vào tivi.m3u cho ID: {tvg_id}\n")
            updated_count += 1
        else:
            print(f"Không tìm thấy tvg-id=\"{tvg_id}\" trong file tivi.m3u.\n")

    if updated_count > 0:
        with open(m3u_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("HOÀN TẤT! Đã ghi file tivi.m3u thành công.")
    else:
        print("Không có thay đổi nào được ghi.")

if __name__ == "__main__":
    update_m3u_file()
