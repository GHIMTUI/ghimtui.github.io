import os
import requests
from channels import CHANNELS

def check_and_resolve_url(url_entry):
      url_lower = url_entry.lower().strip()    
    # Kiểm tra xem link có bắt đầu bằng 'get:' hoặc 'get ' hay không
    if url_lower.startswith("get:"):
        is_get = True
        raw_url = url_entry[4:].strip() # Cắt bỏ 4 ký tự 'get:'
    elif url_lower.startswith("get "):
        is_get = True
        raw_url = url_entry[4:].strip() # Cắt bỏ 4 ký tự 'get '
    else:
        is_get = False
        raw_url = url_entry.strip()
        
    target_url = raw_url
    if is_get:
        # Code xử lý lấy link stream giữ nguyên...
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

def update_channels():
    updated_channels = {}
    m3u_lines = ["#EXTM3U\n"]

    for channel_name, data in CHANNELS.items():
        urls = data.get("url", [])
        
        # Lấy tvg_id từ channels.py (nếu không có thì lấy tạm tên kênh)
        tvg_id = data.get("tvg_id", channel_name)
        
        # Lấy thêm logo hoặc group nếu bạn có cấu hình trong channels.py
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
            
            clean_stream_url = working_url[4:].strip() if working_url.startswith("get ") else working_url.strip()
            
            updated_channels[channel_name] = data
            updated_channels[channel_name]["url"] = urls

            # Bổ sung đúng chuẩn M3U: dùng dấu gạch ngang tvg-id, tvg-name, tvg-logo
            extinf = f'#EXTINF:-1 tvg-id="{tvg_id}" tvg-name="{channel_name}"'
            if tvg_logo:
                extinf += f' tvg-logo="{tvg_logo}"'
            if group_title:
                extinf += f' group-title="{group_title}"'
            
            # Tên hiển thị của kênh trên ứng dụng (sau dấu phẩy)
            extinf += f',{channel_name.upper()}\n'

            m3u_lines.append(extinf)
            m3u_lines.append(f'{clean_stream_url}\n')
        else:
            print(f"Cảnh báo: Kênh {channel_name} không có link nào hoạt động!")
            updated_channels[channel_name] = data

    # Ghi lại file channels.py
    with open("channels.py", "w", encoding="utf-8") as f:
        f.write("CHANNELS = " + repr(updated_channels) + "\n")

    # Ghi file tivi.m3u
    with open("tivi.m3u", "w", encoding="utf-8") as f:
        f.writelines(m3u_lines)

    print("Cập nhật channels.py và tivi.m3u hoàn tất!")

if __name__ == "__main__":
    update_channels()