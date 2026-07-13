import os
import re
import requests

# 1. Định nghĩa danh sách các kênh cần lấy và mã tvg-id tương ứng trong file m3u
CHANNELS = {
    "sctv3": {"url": "http://vmttv.dpdns.org/VTVGo/?sctv3", "tvg_id": "sctv3hd"},
    "sctv4": {"url": "http://vmttv.dpdns.org/VTVGo/?sctv4", "tvg_id": "sctv4hd"},
    "sctv7": {"url": "http://vmttv.dpdns.org/VTVGo/?sctv7", "tvg_id": "sctv7hd"},
    "sctv8": {"url": "http://vmttv.dpdns.org/VTVGo/?sctv8", "tvg_id": "sctv8hd"},
    "sctv9": {"url": "http://vmttv.dpdns.org/VTVGo/?sctv9", "tvg_id": "sctv9hd"},
    "sctv11": {"url": "http://vmttv.dpdns.org/VTVGo/?sctv11", "tvg_id": "sctv11hd"},
    "sctv12": {"url": "http://vmttv.dpdns.org/VTVGo/?sctv12", "tvg_id": "sctv12hd"},
    "sctv13": {"url": "http://vmttv.dpdns.org/VTVGo/?sctv13", "tvg_id": "sctv13hd"},
    "sctv14": {"url": "http://vmttv.dpdns.org/VTVGo/?sctv14", "tvg_id": "sctv14hd"},
    "sctv18": {"url": "http://vmttv.dpdns.org/VTVGo/?sctv18", "tvg_id": "sctv18hd"},
    "sctv19": {"url": "http://vmttv.dpdns.org/VTVGo/?sctv19", "tvg_id": "sctv19hd"},
    "sctv21": {"url": "http://vmttv.dpdns.org/VTVGo/?sctv21", "tvg_id": "sctv21hd"},
    "sctvphim": {"url": "http://vmttv.dpdns.org/VTVGo/?sctvphim", "tvg_id": "sctvhdpth"},
}

FILE_NAME = "tivi.m3u"

def get_live_link(url, channel_name):
    try:
        # Gửi request và đi theo redirect để lấy link thực tế mới nhất
        response = requests.get(url, timeout=15, allow_redirects=True)
        final_url = response.url
        
        # Bắt buộc chuyển đổi đầu link https thành http
        if final_url.startswith("https://"):
            final_url = final_url.replace("https://", "http://", 1)
            
        print(f"[{channel_name.upper()}] Đã lấy được link (HTTP): {final_url}")
        return final_url
    except Exception as e:
        print(f"[{channel_name.upper()}] Lỗi khi kết nối lấy link: {e}")
        return None

def update_m3u_file():
    if not os.path.exists(FILE_NAME):
        print(f"Lỗi: Không tìm thấy file {FILE_NAME} trong thư mục để sửa đổi.")
        return

    # Đọc toàn bộ nội dung hiện tại của file tivi.m3u
    with open(FILE_NAME, "r", encoding="utf-8") as f:
        content = f.read()

    has_changed = False

    # Duyệt qua từng kênh để tìm và thay thế link
    for channel_name, config in CHANNELS.items():
        tvg_id = config["tvg_id"]
        source_url = config["url"]
        
        # Lấy link stream mới dạng http
        new_link = get_live_link(source_url, channel_name)
        if not new_link:
            continue

        # Regex tìm cụm cấu hình của tvg-id và dòng link ngay phía sau nó (chấp nhận cả http và https cũ)
        pattern = rf'(#EXTINF:[^\n]*tvg-id="{tvg_id}"[^\n]*\n(?:#KODIPROP:[^\n]*\n)*)(https?://[^\n]+)'

        if re.search(pattern, content, re.IGNORECASE):
            content, count = re.subn(pattern, rf'\1{new_link}', content, flags=re.IGNORECASE)
            if count > 0:
                print(f"--> Đã cập nhật thành công link cho {channel_name.upper()}")
                has_changed = True
        else:
            print(f"--> Cảnh báo: Không tìm thấy cấu trúc kênh {channel_name.upper()} với tvg-id=\"{tvg_id}\" trong m3u.")

    # Ghi đè file nếu có sự thay đổi
    if has_changed:
        with open(FILE_NAME, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"\n Hoàn tất! Toàn bộ link dạng HTTP đã được cập nhật vào {FILE_NAME}.")
    else:
        print("\n Không có thay đổi nào được thực hiện.")

if __name__ == "__main__":
    update_m3u_file()
