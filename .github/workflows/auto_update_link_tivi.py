import os
import re
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
        # Cấu trúc: ("link m3u8", "link referer", "mã key", "Getlink or No")
        url = ""
        referer = ""
        license_key = ""
        action_type = "Getlink"

        if isinstance(item, tuple):
            if len(item) >= 4:
                url, referer, license_key, action_type = item[:4]
            elif len(item) == 3:
                url, referer, license_key = item
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

        try:
            headers = {}
            if referer:
                headers["Referer"] = referer

            # Đối với link cấu hình "No" (thường là .mpd), ta dùng stream=True hoặc timeout ngắn 
            # để check xem server có phản hồi hay chết hẳn (404) không.
            response = requests.get(url, headers=headers, timeout=10, allow_redirects=True, stream=True)

            # Nếu là chế độ "No": Miễn là server không trả về lỗi 404 (Not Found) hay 410, 
            # ta coi như link còn sống và chấp nhận dùng nó luôn.
            if is_no_mode:
                if response.status_code != 404 and response.status_code != 410:
                    print(f"[{ch_upper}] Link {idx} (No) hợp lệ (HTTP {response.status_code}), sử dụng trực tiếp.")
                    return url, referer, license_key
                else:
                    print(f"[{ch_upper}] Link {idx} (No) đã chết (HTTP {response.status_code}), chuyển sang link dự phòng...")
                    continue

            # Xử lý bình thường cho các link Getlink (m3u8)
            if response.status_code == 200:
                final_url = response.url

                if "master.m3u8" in final_url:
                    final_url = final_url.replace("master.m3u8", "playlist_720p.m3u8")

                print(f"[{ch_upper}] Thành công với link {idx}: {final_url}")
                return final_url, referer, license_key
            
            print(f"[{ch_upper}] Link {idx} trả về mã lỗi HTTP {response.status_code}")

        except Exception as e:
            print(f"[{ch_upper}] Lỗi khi kết nối link {idx}: {e}")

    print(f"[{ch_upper}] Tất cả các link đều thất bại.")
    return None, None, None

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
        
        new_link, new_referer, new_license = get_live_link(config["url"], channel_name)
        if not new_link:
            continue

        def make_replacement(match):
            extinf_part = match.group(1)
            opt_part = match.group(2) or ""
            other_tags = match.group(3) or ""
            
            # 1. Xử lý Referer
            if new_referer:
                referer_line = f"#EXTVLCOPT:http-user-referer={new_referer}\n"
                if "#EXTVLCOPT:http-user-referer=" in extinf_part + opt_part + other_tags:
                    combined = extinf_part + opt_part + other_tags
                    combined = re.sub(r'#EXTVLCOPT:http-user-referer=[^\r\n]*\r?\n', referer_line, combined, flags=re.IGNORECASE)
                    opt_part = combined[len(extinf_part):]
                    other_tags = ""
                else:
                    opt_part += referer_line

            # 2. Xử lý Kodi Properties cho ClearKey (tự động đi kèm license_type và license_key)
            if new_license:
                type_line = "#KODIPROP:inputstream.adaptive.license_type=clearkey\n"
                key_line = f"#KODIPROP:inputstream.adaptive.license_key={new_license}\n"
                
                combined = extinf_part + opt_part + other_tags
                
                # Xóa các dòng license cũ nếu đã tồn tại để tránh bị lặp
                combined = re.sub(r'#KODIPROP:inputstream\.adaptive\.license_type=[^\r\n]*\r?\n', '', combined, flags=re.IGNORECASE)
                combined = re.sub(r'#KODIPROP:inputstream\.adaptive\.license_key=[^\r\n]*\r?\n', '', combined, flags=re.IGNORECASE)
                
                # Chèn bộ đôi dòng lệnh clearkey mới vào nhóm các tag phụ
                other_tags = type_line + key_line
                opt_part = combined[len(extinf_part):]

            return f"{extinf_part}{opt_part}{other_tags}{new_link}"

        # 1. Tìm và thay thế theo tvg-id
        pattern = rf'(#EXTINF:[^\r\n]*tvg-id\s*=\s*["\']{re.escape(tvg_id)}["\'][^\r\n]*\r?\n)((?:#EXTVLCOPT:[^\r\n]*\r?\n)?)((?:#[^\r\n]+\r?\n)*)(https?://[^\r\n]+)'
        
        if re.search(pattern, content, flags=re.IGNORECASE):
            content, count = re.subn(pattern, make_replacement, content, count=1, flags=re.IGNORECASE)
            if count > 0:
                print(f"--> Đã cập nhật link, referer và clearkey cho {ch_upper}")
                has_changed = True
                continue

        # 2. Fallback phụ theo tên kênh hoặc tvg-name
        fallback_pattern = rf'(#EXTINF:[^\r\n]*(?:tvg-name|channel-title)\s*=\s*["\'][^"\']*{re.escape(channel_name)}[^"\']*["\'][^\r\n]*\r?\n)((?:#EXTVLCOPT:[^\r\n]*\r?\n)?)((?:#[^\r\n]+\r?\n)*)(https?://[^\r\n]+)'
        
        if re.search(fallback_pattern, content, flags=re.IGNORECASE):
            content, count = re.subn(fallback_pattern, make_replacement, fallback_pattern, count=1, flags=re.IGNORECASE) # fixed inside function call below
            # Lưu ý đoạn subn chuẩn:
            content, count = re.subn(fallback_pattern, make_replacement, content, count=1, flags=re.IGNORECASE)
            if count > 0:
                print(f"--> Đã cập nhật link, referer và clearkey cho {ch_upper} (khớp qua tên kênh dự phòng)")
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
