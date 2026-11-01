import os
import re
import sys
import concurrent.futures
import requests
from slow_channels import SLOW_CHANNELS

CHANNELS = SLOW_CHANNELS
FAST_CHANNELS = [""]
FILE_NAME = "tivi.m3u"

def get_live_link(urls_config, channel_name):
    if isinstance(urls_config, str):
        urls_config = [(urls_config, "", "", "Getlink")]

    ch_upper = channel_name.upper()

    for idx, item in enumerate(urls_config, 1):
        url = ""
        referer = ""
        license_key = ""
        action_type = "Getlink"

        if isinstance(item, tuple):
            if len(item) >= 4:
                url, referer, license_key, action_type = item[:4]
            elif len(item) == 3:
                url, referer, third_val = item
                if str(third_val).strip().lower() in ["getlink", "no"]:
                    action_type = third_val
                    license_key = ""
                else:
                    license_key = third_val
            elif len(item) == 2:
                url, second_val = item
                if str(second_val).strip().lower() in ["getlink", "no"]:
                    action_type = second_val
                else:
                    referer = second_val
            elif len(item) == 1:
                url = item[0]
        else:
            url = item

        is_no_mode = str(action_type).strip().lower() == "no"

        if is_no_mode:
            print(f"[{ch_upper}] Đang kiểm tra nhanh link {idx} (Cấu hình No/DASH): {url}")
        else:
            print(f"[{ch_upper}] Đang thử link {idx} (Getlink): {url}")
        sys.stdout.flush()

        try:
            headers = {}
            if referer:
                headers["Referer"] = referer

            response = requests.get(url, headers=headers, timeout=8, allow_redirects=True, stream=True)

            if is_no_mode:
                if response.status_code not in [404, 410]:
                    print(f"[{ch_upper}] Link {idx} (No) hợp lệ (HTTP {response.status_code}), sử dụng trực tiếp.")
                    sys.stdout.flush()
                    return url, referer, license_key
                else:
                    print(f"[{ch_upper}] Link {idx} (No) đã chết (HTTP {response.status_code}), chuyển sang link dự phòng...")
                    sys.stdout.flush()
                    continue

            if response.status_code == 200:
                final_url = response.url
                if "master.m3u8" in final_url:
                    final_url = final_url.replace("master.m3u8", "playlist_720p.m3u8")

                print(f"[{ch_upper}] Thành công với link {idx}: {final_url}")
                sys.stdout.flush()
                return final_url, referer, license_key
            
            print(f"[{ch_upper}] Link {idx} trả về mã lỗi HTTP {response.status_code}")
            sys.stdout.flush()

        except Exception as e:
            print(f"[{ch_upper}] Lỗi khi kết nối link {idx}: {e}")
            sys.stdout.flush()

    print(f"[{ch_upper}] Tất cả các link đều thất bại.")
    sys.stdout.flush()
    return None, None, None

def process_single_channel(channel_name, config):
    """Hàm xử lý lấy link cho từng kênh (dùng để chạy đa luồng)"""
    tvg_id = config.get("tvg_id", "")
    new_link, new_referer, new_license = get_live_link(config["url"], channel_name)
    return channel_name, tvg_id, new_link, new_referer, new_license

def update_m3u_file():
    if not os.path.exists(FILE_NAME):
        print(f"Lỗi: Không tìm thấy file {FILE_NAME} trong thư mục để sửa đổi.")
        sys.stdout.flush()
        return

    update_type = os.getenv("UPDATE_TYPE", "all").lower()
    print(f"Chế độ lọc kênh hoạt động: {update_type.upper()}")
    sys.stdout.flush()

    if update_type == "fast":
        channels_to_update = {k: v for k, v in CHANNELS.items() if k in FAST_CHANNELS}
    elif update_type == "slow":
        channels_to_update = {k: v for k, v in CHANNELS.items() if k not in FAST_CHANNELS}
    else:
        channels_to_update = CHANNELS

    if not channels_to_update:
        print("Không có kênh nào cần cập nhật trong lượt này.")
        sys.stdout.flush()
        return

    # 1. Quét song song tất cả các kênh bằng ThreadPoolExecutor (Tăng tốc độ kiểm tra mạng cực lớn)
    print(f"\nBắt đầu quét đồng thời {len(channels_to_update)} kênh...")
    sys.stdout.flush()

    results = []
    # max_workers=10 nghĩa là chạy tối đa 10 luồng cùng lúc, bạn có thể tăng lên 15 hoặc 20 nếu mạng khỏe
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_channel = {
            executor.submit(process_single_channel, ch_name, ch_conf): ch_name 
            for ch_name, ch_conf in channels_to_update.items()
        }
        for future in concurrent.futures.as_completed(future_to_channel):
            try:
                res = future.result()
                if res[2]: # Nếu có new_link
                    results.append(res)
            except Exception as exc:
                print(f"Lỗi luồng xử lý kênh: {exc}")

    if not results:
        print("\nKhông có kênh nào lấy được link mới hợp lệ.")
        sys.stdout.flush()
        return

    # 2. Đọc nội dung file m3u 1 lần duy nhất
    with open(FILE_NAME, "r", encoding="utf-8") as f:
        content = f.read()

    any_changed = False

    # 3. Tiến hành thay thế hàng loạt trên nội dung chuỗi trong RAM
    for channel_name, tvg_id, new_link, new_referer, new_license in results:
        ch_upper = channel_name.upper()
        channel_changed = False

        def make_replacement(match):
            extinf_part = match.group(1)
            opt_part = match.group(2) or ""
            other_tags = match.group(3) or ""
            
            # Xử lý Referer
            if new_referer:
                referer_line = f"#EXTVLCOPT:http-user-referer={new_referer}\n"
                if "#EXTVLCOPT:http-user-referer=" in extinf_part + opt_part + other_tags:
                    combined = extinf_part + opt_part + other_tags
                    combined = re.sub(r'#EXTVLCOPT:http-user-referer=[^\r\n]*\r?\n', referer_line, combined, flags=re.IGNORECASE)
                    opt_part = combined[len(extinf_part):]
                    other_tags = ""
                else:
                    opt_part += referer_line

            # Xử lý Kodi Properties cho ClearKey
            cleaned_license = str(new_license).strip()
            if cleaned_license and cleaned_license.lower() not in ["getlink", "no"]:
                type_line = "#KODIPROP:inputstream.adaptive.license_type=clearkey\n"
                key_line = f"#KODIPROP:inputstream.adaptive.license_key={cleaned_license}\n"
                
                combined = extinf_part + opt_part + other_tags
                combined = re.sub(r'#KODIPROP:inputstream\.adaptive\.license_type=[^\r\n]*\r?\n', '', combined, flags=re.IGNORECASE)
                combined = re.sub(r'#KODIPROP:inputstream\.adaptive\.license_key=[^\r\n]*\r?\n', '', combined, flags=re.IGNORECASE)
                
                other_tags = type_line + key_line
                opt_part = combined[len(extinf_part):]
            else:
                combined = extinf_part + opt_part + other_tags
                combined = re.sub(r'#KODIPROP:inputstream\.adaptive\.license_type=[^\r\n]*\r?\n', '', combined, flags=re.IGNORECASE)
                combined = re.sub(r'#KODIPROP:inputstream\.adaptive\.license_key=[^\r\n]*\r?\n', '', combined, flags=re.IGNORECASE)
                opt_part = combined[len(extinf_part):]
                other_tags = ""

            return f"{extinf_part}{opt_part}{other_tags}{new_link}"

        # Tìm theo tvg-id
        pattern = rf'(#EXTINF:[^\r\n]*tvg-id\s*=\s*["\']{re.escape(tvg_id)}["\'][^\r\n]*\r?\n)((?:#EXTVLCOPT:[^\r\n]*\r?\n)?)((?:#[^\r\n]+\r?\n)*)(https?://[^\r\n]+)'
        if re.search(pattern, content, flags=re.IGNORECASE):
            content, count = re.subn(pattern, make_replacement, content, count=1, flags=re.IGNORECASE)
            if count > 0:
                print(f"--> Đã cập nhật link và referer cho {ch_upper}")
                channel_changed = True

        # Fallback theo tên kênh nếu không khớp tvg-id
        if not channel_changed:
            fallback_pattern = rf'(#EXTINF:[^\r\n]*(?:tvg-name|channel-title)\s*=\s*["\'][^"\']*{re.escape(channel_name)}[^"\']*["\'][^\r\n]*\r?\n)((?:#EXTVLCOPT:[^\r\n]*\r?\n)?)((?:#[^\r\n]+\r?\n)*)(https?://[^\r\n]+)'
            if re.search(fallback_pattern, content, flags=re.IGNORECASE):
                content, count = re.subn(fallback_pattern, make_replacement, content, count=1, flags=re.IGNORECASE)
                if count > 0:
                    print(f"--> Đã cập nhật link và referer cho {ch_upper} (khớp qua tên kênh dự phòng)")
                    channel_changed = True

        if channel_changed:
            any_changed = True
        else:
            print(f'--> Cảnh báo: Không tìm thấy cấu trúc kênh {ch_upper} với tvg-id="{tvg_id}" trong m3u.')
            sys.stdout.flush()

    # 4. Ghi file 1 lần duy nhất vào cuối quá trình
    if any_changed:
        with open(FILE_NAME, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"\n--> Đã ghi lưu toàn bộ kết quả vào {FILE_NAME}")
        print("\nHoàn tất toàn bộ quá trình cập nhật các kênh!")
    else:
        print("\nKhông có thay đổi nào được thực hiện trên file.")
    sys.stdout.flush()

if __name__ == "__main__":
    update_m3u_file()
