import os
import re
import requests

# 1. Định nghĩa danh sách các kênh cần lấy và mã tvg-id tương ứng trong file m3u
CHANNELS = {
    "sctv2": {"url": "http://vmttv.dpdns.org/VTVGo/?sctv2", "tvg_id": "sctv2hd"},
    "sctv4": {"url": "http://vmttv.dpdns.org/VTVGo/?sctv4", "tvg_id": "sctv4hd"},
    "sctv7": {"url": "http://vmttv.dpdns.org/VTVGo/?sctv7", "tvg_id": "sctv7hd"},
    "sctv11": {"url": "http://vmttv.dpdns.org/VTVGo/?sctv11", "tvg_id": "sctv11hd"},
    "sctv13": {"url": "http://vmttv.dpdns.org/VTVGo/?sctv13", "tvg_id": "sctv13hd"},
    "sctv16": {"url": "http://vmttv.dpdns.org/VTVGo/?sctv16", "tvg_id": "sctv16hd"},
    "sctv18": {"url": "http://vmttv.dpdns.org/VTVGo/?sctv18", "tvg_id": "sctv18hd"},
    "sctvphim": {"url": "http://vmttv.dpdns.org/VTVGo/?sctvphim", "tvg_id": "sctvhdpth"},
   }

# Danh sách phân loại kênh theo tần suất
FAST_CHANNELS = [""]

FILE_NAME = "tivi.m3u"

def get_live_link(url, channel_name):
    try:
        response = requests.get(url, timeout=15, allow_redirects=True)
        final_url = response.url
        
        # Bắt buộc chuyển đổi đầu link https thành http
        if final_url.startswith("https://"):
            final_url = final_url.replace("https://", "http://", 1)
            
        # Logic thay đổi đuôi master.m3u8 thành playlist phù hợp
        if "master.m3u8" in final_url:
            if channel_name.lower() == "sctvphim":
                final_url = final_url.replace("master.m3u8", "playlist_1080p.m3u8")
            else:
                final_url = final_url.replace("master.m3u8", "playlist_720p.m3u8")
            
        print(f"[{channel_name.upper()}] Đã lấy được link: {final_url}")
        return final_url
    except Exception as e:
        print(f"[{channel_name.upper()}] Lỗi khi kết nối lấy link: {e}")
        return None

def update_m3u_file():
    if not os.path.exists(FILE_NAME):
        print(f"Lỗi: Không tìm thấy file {FILE_NAME} trong thư mục để sửa đổi.")
        return

    # Lấy chế độ chạy từ môi trường GitHub Actions gửi xuống (mặc định là 'all')
    update_type = os.getenv("UPDATE_TYPE", "all")
    print(f"Chế độ lọc kênh hoạt động: {update_type.upper()}")

    # Lọc danh sách kênh cần cập nhật dựa trên chế độ
    channels_to_update = {}
    for name, config in CHANNELS.items():
        if update_type == "fast":
            # Chỉ lấy các kênh thuộc nhóm 3h
            if name in FAST_CHANNELS:
                channels_to_update[name] = config
        elif update_type == "slow":
            # Bỏ qua các kênh thuộc nhóm 3h, chỉ lấy các kênh còn lại
            if name not in FAST_CHANNELS:
                channels_to_update[name] = config
        else:
            # Chạy 'all' khi kích hoạt thủ công
            channels_to_update[name] = config

    if not channels_to_update:
        print("Không có kênh nào cần cập nhật trong lượt này.")
        return

    # Đọc toàn bộ nội dung hiện tại của file tivi.m3u
    with open(FILE_NAME, "r", encoding="utf-8") as f:
        content = f.read()

    has_changed = False

    # Chỉ duyệt qua các kênh đã được lọc
    for channel_name, config in channels_to_update.items():
        tvg_id = config["tvg_id"]
        source_url = config["url"]
        
        new_link = get_live_link(source_url, channel_name)
        if not new_link:
            continue

        pattern = rf'(#EXTINF:[^\n]*tvg-id="{tvg_id}"[^\n]*\n(?:#KODIPROP:[^\n]*\n)*)(https?://[^\n]+)'

        if re.search(pattern, content, re.IGNORECASE):
            content, count = re.subn(pattern, rf'\1{new_link}', content, flags=re.IGNORECASE)
            if count > 0:
                print(f"--> Đã cập nhật link {channel_name.upper()}")
                has_changed = True
        else:
            print(f"--> Cảnh báo: Không tìm thấy cấu trúc kênh {channel_name.upper()} với tvg-id=\"{tvg_id}\" trong m3u.")

    if has_changed:
        with open(FILE_NAME, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"\n Hoàn tất! Đã lưu các thay đổi vào {FILE_NAME}.")
    else:
        print("\n Không có thay đổi nào được thực hiện  trên file.")

if __name__ == "__main__":
    update_m3u_file()
