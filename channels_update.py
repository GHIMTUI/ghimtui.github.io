import re
import requests
from channels import CHANNELS

def check_link_alive(url):
    """Kiểm tra xem link m3u8 hoặc vỏ bọc có hoạt động không"""
    try:
        # Sử dụng phương thức GET hoặc HEAD tùy nguồn, timeout 10 giây
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, timeout=10, stream=True)
        # Chấp nhận mã trạng thái 200 hoặc các mã chuyển hướng thành công
        if response.status_code == 200:
            return True
    except Exception as e:
        print(f"Link lỗi hoặc không phản hồi: {url} | Lỗi: {e}")
    return False

def get_active_url(url_list):
    """Kiểm tra danh sách link theo thứ tự, link1 chết chuyển sang link2"""
    if isinstance(url_list, str):
        return url_list
        
    for idx, url in enumerate(url_list):
        print(f"Đang kiểm tra link {idx + 1}: {url}")
        if check_link_alive(url):
            print(f"-> Link {idx + 1} SỐNG. Đã chọn.")
            return url
        else:
            print(f"-> Link {idx + 1} CHẾT. Đang chuyển...")
            
    # Nếu tất cả đều chết, trả về link đầu tiên làm mặc định hoặc None tùy ý bạn
    print("Cảnh báo: Tất cả các link đều chết, giữ lại link đầu tiên.")
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
        
        # Lấy link đang sống từ danh sách (Ưu tiên link1, chết đổi sang link2...)
        active_url = get_active_url(url_list)
        if not active_url:
            continue

        # Biểu thức chính quy tìm đúng dòng định nghĩa kênh có tvg-id và thay thế link vỏ bọc phía dưới
        pattern = re.compile(rf'(#EXTINF:[^\n]*tvg-id="{tvg_id}"[^\n]*\n)([^\n#]+)', re.IGNORECASE)
        
        if pattern.search(content):
            content = pattern.sub(rf'\1{active_url}', content)
            print(f"Đã cập nhật thành công link cho: {tvg_id} -> {active_url}\n")
            updated_count += 1
        else:
            print(f"Không tìm thấy tvg-id=\"{tvg_id}\" trong file m3u.\n")

    if updated_count > 0:
        with open(m3u_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("Đã lưu lại file tivi.m3u thành công.")
    else:
        print("Không có thay đổi nào được ghi vào file.")

if __name__ == "__main__":
    update_m3u_file()
