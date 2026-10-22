import os
import re
import requests
from slow_channels import SLOW_CHANNELS

CHANNELS = SLOW_CHANNELS
FAST_CHANNELS = [""]
FILE_NAME = "tivi.m3u"

def get_live_link(urls, channel_name):
    if isinstance(urls, str):
        urls = [urls]

    ch_upper = channel_name.upper()
    ch_lower = channel_name.lower()

    for idx, url in enumerate(urls, 1):
        try:
            print(f"[{ch_upper}] Đang thử link {idx}: {url}")
            response = requests.get(url, timeout=15, allow_redirects=True)

            if response.status_code == 200:
                final_url = response.url

                if "master.m3u8" in final_url:
                    if ch_lower == "sctvphim":
                        final_url = final_url.replace("master.m3u8", "playlist_1080p.m3u8")
                    elif ch_lower != "sctv14":
                        final_url = final_url.replace("master.m3u8", "playlist_720p.m3u8")

                print(f"[{ch_upper}] Thành công với link {idx}: {final_url}")
                return final_url
            
            print(f"[{ch_upper}] Link {idx} trả về mã lỗi HTTP {response.status_code}")
        except Exception as e:
            print(f"[{ch_upper}] Lỗi khi kết nối link {idx}: {e}")

    print(f"[{ch_upper}] Tất cả các link dự phòng đều thất bại.")
    return None

def update_m3u_file():
    if not os.path.exists(FILE_NAME):
        print(f"Lỗi: Không tìm thấy file {FILE_NAME} trong thư mục để sửa đổi.")
        return

    update_type = os.getenv("UPDATE_TYPE", "all").lower()
    print(f"Chế độ lọc kênh hoạt động: {update_type.upper()}")

    # Lọc kênh gọn gàng hơn
    if update_type == "fast":
        channels_to_update = {k: v for k, v in CHANNELS.items() if k in FAST_CHANNELS}
    elif update_type == "slow":
        channels_to_update = {k: v for k, v in CHANNELS.items() if k not in FAST_CHANNELS}
    else:
        channels_to_update = CHANNELS

    if not channels_to_update:
        print("Không có kênh nào cần cập nhật trong lượt này.")
        return

    with open(FILE_NAME, "r", encoding="utf-8") as f:
        content = f.read()

    has_changed = False

    for channel_name, config in channels_to_update.items():
        tvg_id = config["tvg_id"]
        ch_upper = channel_name.upper()
        
        new_link = get_live_link(config["url"], channel_name)
        if not new_link:
            continue

        # 1. Thử tìm và thay thế theo tvg-id
        pattern = rf'(#EXTINF:[^\r\n]*tvg-id\s*=\s*["\']{re.escape(tvg_id)}["\'][^\r\n]*\r?\n(?:#[^\r\n]+\r?\n)*)(https?://[^\r\n]+)'
        content, count = re.subn(pattern, rf'\1{new_link}', content, flags=re.IGNORECASE)

        if count > 0:
            print(f"--> Đã cập nhật link {ch_upper}")
            has_changed = True
            continue

        # 2. Fallback phụ: Thử tìm theo tên kênh hoặc tvg-name
        fallback_pattern = rf'(#EXTINF:[^\r\n]*(?:tvg-name|channel-title)\s*=\s*["\'][^"\']*{re.escape(channel_name)}[^"\']*["\'][^\r\n]*\r?\n(?:#[^\r\n]+\r?\n)*)(https?://[^\r\n]+)'
        content, count = re.subn(fallback_pattern, rf'\1{new_link}', content, flags=re.IGNORECASE)

        if count > 0:
            print(f"--> Đã cập nhật link {ch_upper} (khớp qua tên kênh dự phòng)")
            has_changed = True
            continue

        print(f'--> Cảnh báo: Không tìm thấy cấu trúc kênh {ch_upper} với tvg-id="{tvg_id}" trong m3u.')

    if has_changed:
        with open(FILE_NAME, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"\nHoàn tất! Đã lưu các thay đổi vào {FILE_NAME}.")
    else:
        print("\nKhông có thay đổi nào được thực hiện trên file.")

if __name__ == "__main__":
    update_m3u_file()
