import os
import requests
from channels import CHANNELS

def check_and_resolve_url(url_entry):
    url_lower = url_entry.lower().strip()
    is_get = False
    raw_url = url_entry.strip()
    
    # Kiểm tra các dạng tiền tố get
    if url_lower.startswith("get:"):
        is_get = True
        raw_url = url_entry[4:].strip()
        if raw_url.startswith(":"): # Phòng hờ trường hợp get::
            raw_url = raw_url[1:].strip()
    elif url_lower.startswith("get "):
        is_get = True
        raw_url = url_entry[4:].strip()

    target_url = raw_url
    if is_get:
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(raw_url, headers=headers, timeout=10, allow_redirects=True)
            if response.status_code == 200:
                content = response.text.strip()
                lines = content.splitlines()
                for line in lines:
                    line = line.strip()
                    if line.startswith("http") and (".m3u8" in line or "live" in line or "stream" in line):
                        target_url = line
                        break
                else:
                    target_url = response.url
        except Exception as e:
            print(f"Lỗi khi get {raw_url}: {e}")
            return url_entry, False

    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.head(target_url, headers=headers, timeout=5, allow_redirects=True)
        if res.status_code >= 400:
            res = requests.get(target_url, headers=headers, timeout=5, stream=True)
        
        if res.status_code < 400:
            return url_entry, True
    except Exception:
        pass

    return url_entry, False

def clean_get_prefix(url_str):
    """ Hàm phụ trợ làm sạch chữ get: hoặc get ở đầu link trước khi in ra m3u """
    u_lower = url_str.lower().strip()
    if u_lower.startswith("get:"):
        clean = url_str[4:].strip()
        if clean.startswith(":"):
            clean = clean[1:].strip()
        return clean
    elif u_lower.startswith("get "):
        return url_str[4:].strip()
    return url_str.strip()

def update_channels():
    updated_channels = {}
    
    # Đọc file tivi.m3u cũ nếu tồn tại để giữ lại các kênh khác không nằm trong CHANNELS.py
    existing_m3u_blocks = {} # key là tvg_id hoặc tên kênh, value là toàn bộ đoạn textEXTINF + URL
    if os.path.exists("tivi.m3u"):
        with open("tivi.m3u", "r", encoding="utf-8") as f:
            content = f.read()
            # Tách các dòng M3U
            lines = content.splitlines()
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                if line.startswith("#EXTINF:"):
                    extinf_line = line
                    stream_line = lines[i+1].strip() if i+1 < len(lines) else ""
                    
                    # Trích xuất tvg-id hoặc tvg-name để làm key nhận diện kênh
                    ident = ""
                    if 'tvg-id="' in extinf_line:
                        try:
                            ident = extinf_line.split('tvg-id="')[1].split('"')[0]
                        except:
                            pass
                    if not ident and 'tvg-name="' in extinf_line:
                        try:
                            ident = extinf_line.split('tvg-name="')[1].split('"')[0]
                        except:
                            pass
                    
                    if ident:
                        existing_m3u_blocks[ident] = (extinf_line, stream_line)
                    i += 2
                else:
                    i += 1

    m3u_lines = ["#EXTM3U\n"]
    processed_ids = set()

    for channel_name, data in CHANNELS.items():
        urls = data.get("url", [])
        tvg_id = data.get("tvg_id", channel_name)
        tvg_logo = data.get("tvg_logo", "")
        group_title = data.get("group_title", "Truyền Hình")

        working_url = None
        working_index = -1

        for idx, url_entry in enumerate(urls):
            print(f"Đang kiểm tra [{channel_name}] (Link {idx}): {url_entry}")
            _, is_alive = check_and_resolve_url(url_entry)
            if is_alive:
                working_url = url_entry
                working_index = idx
                print(f"-> Thành công ở link {idx}!")
                break
            else:
                print(f"-> Mất tín hiệu, chuyển sang link tiếp theo...")

        if working_url:
            urls.pop(working_index)
            urls.insert(0, working_url)
            
            updated_channels[channel_name] = data
            updated_channels[channel_name]["url"] = urls

            # Làm sạch tiền tố get để lấy đúng link stream cuối cùng in ra file m3u
            clean_stream_url = clean_get_prefix(working_url)

            extinf = f'#EXTINF:-1 tvg-id="{tvg_id}" tvg-name="{channel_name}"'
            if tvg_logo:
                extinf += f' tvg-logo="{tvg_logo}"'
            if group_title:
                extinf += f' group-title="{group_title}"'
            extinf += f',{channel_name.upper()}'

            # Cập nhật hoặc thêm mới vào bộ nhớ m3u theo đúng tvg_id
            existing_m3u_blocks[tvg_id] = (extinf, clean_stream_url)
            processed_ids.add(tvg_id)
        else:
            print(f"Cảnh báo: Kênh {channel_name} không có link nào hoạt động!")
            updated_channels[channel_name] = data

    # Tổng hợp lại file tivi.m3u (Giữ lại các kênh cũ khác, cập nhật đúng các kênh có trong CHANNELS)
    for ident, (extinf, stream_url) in existing_m3u_blocks.items():
        m3u_lines.append(f"{extinf}\n")
        m3u_lines.append(f"{stream_url}\n")

    # Ghi lại file channels.py
    with open("channels.py", "w", encoding="utf-8") as f:
        f.write("CHANNELS = " + repr(updated_channels) + "\n")

    # Ghi lại file tivi.m3u mà không làm mất các kênh khác
    with open("tivi.m3u", "w", encoding="utf-8") as f:
        f.writelines(m3u_lines)

    print("Cập nhật channels.py và tivi.m3u hoàn tất!")

if __name__ == "__main__":
    update_channels()
