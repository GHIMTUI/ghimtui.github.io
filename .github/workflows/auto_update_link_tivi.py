import os
import re
import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from slow_channels import SLOW_CHANNELS

CHANNELS = SLOW_CHANNELS
FAST_CHANNELS = [""]
FILE_NAME = "tivi.m3u"

def test_url_speed(idx, item, channel_name):
    """Hàm kiểm tra tốc độ phản hồi của một link kèm theo số thứ tự idx"""
    ch_upper = channel_name.upper()
    
    if isinstance(item, tuple):
        url, action_type = item
    else:
        url, action_type = item, "Getlink"

    # Nếu cấu hình là "No" thì bỏ qua
    if str(action_type).strip().lower() == "no":
        print(f"[{ch_upper}] Link {idx}: Cấu hình No, bỏ qua không test.")
        return None

    try:
        print(f"[{ch_upper}] Đang test tốc độ link {idx}: {url}")
        start_time = time.time()
        response = requests.get(url, timeout=12, allow_redirects=True)
        elapsed_time = time.time() - start_time

        if response.status_code == 200:
            final_url = response.url
            if "master.m3u8" in final_url:
                final_url = final_url.replace("master.m3u8", "playlist_720p.m3u8")
            
            print(f"[{ch_upper}] Link {idx} {elapsed_time:.2f}s thành công: {final_url}")
            return (idx, final_url, elapsed_time)
        else:
            print(f"--> Link {idx} lỗi HTTP {response.status_code}")
    except Exception as e:
        print(f"--> Lỗi kết nối link {idx}")
    
    return None

def get_fastest_live_link(urls_config, channel_name):
    if isinstance(urls_config, str):
        urls_config = [(urls_config, "Getlink")]

    ch_upper = channel_name.upper()
    valid_results = []

    # Sử dụng ThreadPoolExecutor để test tất cả các link song song kèm theo index (bắt đầu từ 1)
    max_workers = min(len(urls_config), 5)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_idx = {
            executor.submit(test_url_speed, idx, item, channel_name): idx 
            for idx, item in enumerate(urls_config, 1)
        }
        
        for future in as_completed(future_to_idx):
            result = future.result()
            if result:
                valid_results.append(result)

    if not valid_results:
        print(f"[{ch_upper}] Tất cả các link đều thất bại hoặc không phản hồi.")
        return None

    # Sắp xếp các link thành công theo thời gian phản hồi tăng dần (nhanh nhất đứng đầu)
    valid_results.sort(key=lambda x: x[2])
    best_idx, fastest_url, best_time = valid_results[0]
    
    print(f"--> Đã chọn link {best_idx}")
    return fastest_url

def update_m3u_file():
    if not os.path.exists(FILE_NAME):
        print(f"Lỗi: Không tìm thấy file {FILE_NAME} trong thư mục để sửa đổi.")
        return

    update_type = os.getenv("UPDATE_TYPE", "all").lower()
    print(f"Chế độ lọc kênh hoạt động: {update_type.upper()}")

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
        tvg_id = config.get("tvg_id", "")
        ch_upper = channel_name.upper()
        
        raw_url_config = config.get("url")
        new_link = get_fastest_live_link(raw_url_config, channel_name)
        if not new_link:
            continue

        # 1. Thử tìm và thay thế theo tvg-id
        pattern = rf'(#EXTINF:[^\r\n]*tvg-id\s*=\s*["\']{re.escape(tvg_id)}["\'][^\r\n]*\r?\n)(?:#EXTVLCOPT[^\r\n]*\r?\n)*https?://[^\r\n]+'
        content, count = re.subn(pattern, rf'\1{new_link}', content, flags=re.IGNORECASE)

        if count > 0:
            print(f"--> Đã cập nhật link {ch_upper}")
            has_changed = True
            continue

        # 2. Fallback phụ: Thử tìm theo tên kênh hoặc tvg-name
        fallback_pattern = rf'(#EXTINF:[^\r\n]*(?:tvg-name|channel-title)\s*=\s*["\'][^"\']*{re.escape(channel_name)}[^"\']*["\'][^\r\n]*\r?\n)(?:#EXTVLCOPT[^\r\n]*\r?\n)*https?://[^\r\n]+'
        content, count = re.subn(fallback_pattern, rf'\1{new_link}', content, flags=re.IGNORECASE)

        if count > 0:
            print(f" --> Đã cập nhật link {ch_upper} (khớp qua tên kênh dự phòng)")
            has_changed = True
            continue

        print(f'--> Cảnh báo: Không tìm thấy cấu trúc kênh {ch_upper} với tvg-id="{tvg_id}" trong m3u.')

    if has_changed:
        with open(FILE_NAME, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"\nHoàn tất! Đã lưu các thay đổi vào {FILE_NAME}.")
    else:
        print("\nNone: Không có thay đổi nào được thực hiện trên file.")

if __name__ == "__main__":
    update_m3u_file()
