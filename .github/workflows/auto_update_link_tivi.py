import os
import re
import requests
from slow_channels import SLOW_CHANNELS

CHANNELS = SLOW_CHANNELS
FAST_CHANNELS = [""]
FILE_NAME = "tivi.m3u"

def get_live_link(urls_config, channel_name):
    if isinstance(urls_config, str):
        urls_config = [(urls_config, "", "Getlink")]

    ch_upper = channel_name.upper()

    for idx, item in enumerate(urls_config, 1):
        # Hỗ trợ các định dạng cấu hình:
        # 1. Chuỗi đơn: "url"
        # 2. Tuple 2 phần tử: ("url", "action") hoặc ("url", "referer")
        # 3. Tuple 3 phần tử: ("url", "referer", "action")
        referer = ""
        action_type = "Getlink"

        if isinstance(item, tuple):
            if len(item) == 3:
                url, referer, action_type = item
            elif len(item) == 2:
                url, second_val = item
                # Nếu phần tử thứ 2 là chuỗi hành động (Getlink/No)
                if str(second_val).strip().lower() in ["getlink", "no"]:
                    action_type = second_val
                else:
                    referer = second_val
            else:
                url = item[0]
        else:
            url = item

        # Nếu là "No" thì bỏ qua không get link này
        if str(action_type).strip().lower() == "no":
            print(f"[{ch_upper}] Link {idx}: Cấu hình No, bỏ qua không get.")
            continue

        try:
            print(f"[{ch_upper}] Đang thử link {idx} (Getlink): {url}")
            
            # Thiết lập header Referer nếu có cấu hình
            headers = {}
            if referer:
                headers["Referer"] = referer

            response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)

            if response.status_code == 200:
                final_url = response.url

                if "master.m3u8" in final_url:
                    final_url = final_url.replace("master.m3u8", "playlist_720p.m3u8")

                print(f"[{ch_upper}] Thành công với link {idx}: {final_url}")
                return final_url, referer
            
            print(f"[{ch_upper}] Link {idx} trả về mã lỗi HTTP {response.status_code}")
        except Exception as e:
            print(f"[{ch_upper}] Lỗi khi kết nối link {idx}: {e}")

    print(f"[{ch_upper}] Tất cả các link được phép Getlink đều thất bại.")
    return None, None

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
        
        new_link, new_referer = get_live_link(config["url"], channel_name)
        if not new_link:
            continue

        # Hàm trợ giúp tạo khối thay thế cho Referer
        def make_replacement(match):
            extinf_part = match.group(1)
            other_tags = match.group(2) or ""
            
            if new_referer:
                # Nếu có referer mới, kiểm tra xem dòng EXTVLCOPT đã có sẵn chưa để thay thế hoặc thêm mới
                referer_line = f"#EXTVLCOPT:http-user-referer={new_referer}\n"
                if "#EXTVLCOPT:http-user-referer=" in extinf_part + other_tags:
                    # Thay thế dòng referer cũ bằng referer mới
                    combined = extinf_part + other_tags
                    combined = re.sub(r'#EXTVLCOPT:http-user-referer=[^\r\n]*\r?\n', referer_line, combined, flags=re.IGNORECASE)
                    return f"{combined}{new_link}"
                else:
                    return f"{extinf_part}{referer_line}{other_tags}{new_link}"
            else:
                # Nếu không có cấu hình referer mới, giữ nguyên dòng referer cũ (nếu có) hoặc bỏ qua
                return f"{extinf_part}{other_tags}{new_link}"

        # 1. Thử tìm và thay thế theo tvg-id
        pattern = rf'(#EXTINF:[^\r\n]*tvg-id\s*=\s*["\']{re.escape(tvg_id)}["\'][^\r\n]*\r?\n)((?:#EXTVLCOPT:[^\r\n]*\r?\n)?)((?:#[^\r\n]+\r?\n)*)(https?://[^\r\n]+)'
        
        # Kiểm tra xem có khớp theo tvg_id không
        if re.search(pattern, content, flags=re.IGNORECASE):
            content, count = re.subn(pattern, make_replacement, content, count=1, flags=re.IGNORECASE)
            if count > 0:
                print(f"--> Đã cập nhật link và referer cho {ch_upper}")
                has_changed = True
                continue

        # 2. Fallback phụ: Thử tìm theo tên kênh hoặc tvg-name
        fallback_pattern = rf'(#EXTINF:[^\r\n]*(?:tvg-name|channel-title)\s*=\s*["\'][^"\']*{re.escape(channel_name)}[^"\']*["\'][^\r\n]*\r?\n)((?:#EXTVLCOPT:[^\r\n]*\r?\n)?)((?:#[^\r\n]+\r?\n)*)(https?://[^\r\n]+)'
        
        if re.search(fallback_pattern, content, flags=re.IGNORECASE):
            content, count = re.subn(fallback_pattern, make_replacement, content, count=1, flags=re.IGNORECASE)
            if count > 0:
                print(f"--> Đã cập nhật link và referer cho {ch_upper} (khớp qua tên kênh dự phòng)")
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
