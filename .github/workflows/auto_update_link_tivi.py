import os
import re
import requests

# Import danh sách từ file dữ liệu riêng
from slow_channels import SLOW_CHANNELS

# Gán CHANNELS bằng SLOW_CHANNELS (hoặc tổng hợp các nguồn kênh khác nếu có)
CHANNELS = SLOW_CHANNELS
FAST_CHANNELS = [""]
FILE_NAME = "tivi.m3u"


def get_live_link(urls, channel_name):
    if isinstance(urls, str):
        urls = [urls]

    for idx, url in enumerate(urls, 1):
        try:
            print(f"[{channel_name.upper()}] Đang thử link {idx}: {url}")
            response = requests.get(url, timeout=15, allow_redirects=True)

            if response.status_code == 200:
                final_url = response.url

                if "master.m3u8" in final_url:
                    ch_name = channel_name.lower()
                    if ch_name == "sctvphim":
                        final_url = final_url.replace(
                            "master.m3u8", "playlist_1080p.m3u8"
                        )
                    elif ch_name != "sctv14":
                        final_url = final_url.replace(
                            "master.m3u8", "playlist_720p.m3u8"
                        )

                print(
                    f"[{channel_name.upper()}] Thành công với link {idx}: {final_url}"
                )
                return final_url
            else:
                print(
                    f"[{channel_name.upper()}] Link {idx} trả về mã lỗi HTTP {response.status_code}"
                )
        except Exception as e:
            print(f"[{channel_name.upper()}] Lỗi khi kết nối link {idx}: {e}")

    print(f"[{channel_name.upper()}] Tất cả các link dự phòng đều thất bại.")
    return None


def update_m3u_file():
    if not os.path.exists(FILE_NAME):
        print(f"Lỗi: Không tìm thấy file {FILE_NAME} trong thư mục để sửa đổi.")
        return

    update_type = os.getenv("UPDATE_TYPE", "all")
    print(f"Chế độ lọc kênh hoạt động: {update_type.upper()}")

    channels_to_update = {}
    for name, config in CHANNELS.items():
        if update_type == "fast":
            if name in FAST_CHANNELS:
                channels_to_update[name] = config
        elif update_type == "slow":
            if name not in FAST_CHANNELS:
                channels_to_update[name] = config
        else:
            channels_to_update[name] = config

    if not channels_to_update:
        print("Không có kênh nào cần cập nhật trong lượt này.")
        return

    with open(FILE_NAME, "r", encoding="utf-8") as f:
        content = f.read()

    has_changed = False

    for channel_name, config in channels_to_update.items():
        tvg_id = config["tvg_id"]
        source_urls = config["url"]

        new_link = get_live_link(source_urls, channel_name)
        if not new_link:
            continue

        pattern = rf'(#EXTINF:[^\n]*tvg-id="{tvg_id}"[^\n]*\n(?:#KODIPROP:[^\n]*\n)*)(https?://[^\n]+)'

        if re.search(pattern, content, re.IGNORECASE):
            content, count = re.subn(
                pattern, rf"\1{new_link}", content, flags=re.IGNORECASE
            )
            if count > 0:
                print(f"--> Đã cập nhật link {channel_name.upper()}")
                has_changed = True
        else:
            print(
                f'--> Cảnh báo: Không tìm thấy cấu trúc kênh {channel_name.upper()} với tvg-id="{tvg_id}" trong m3u.'
            )

    if has_changed:
        with open(FILE_NAME, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"\n Hoàn tất! Đã lưu các thay đổi vào {FILE_NAME}.")
    else:
        print("\n Không có thay đổi nào được thực hiện trên file.")


if __name__ == "__main__":
    update_m3u_file()
