import urllib.request
import re

# Cấu hình map giữa tvg-id trong file m3u và link lấy nguồn
CHANNELS = {
    "sctvhdpth": "https://hoiquan.dpdns.org/VTVGo/?sctvphim",
    "sctv1hd": "https://hoiquan.dpdns.org/VTVGo/?sctv1",
    "sctv4hd": "https://hoiquan.dpdns.org/VTVGo/?sctv4",
    "sctv7hd": "https://hoiquan.dpdns.org/VTVGo/?sctv7",
    "sctv8hd": "https://hoiquan.dpdns.org/VTVGo/?sctv8",
    "sctv11hd": "https://hoiquan.dpdns.org/VTVGo/?sctv11",
    "sctv13hd": "https://hoiquan.dpdns.org/VTVGo/?sctv13",
    "sctv14hd": "https://hoiquan.dpdns.org/VTVGo/?sctv14",
    "sctv18hd": "https://hoiquan.dpdns.org/VTVGo/?sctv18",
    "sctv19hd": "https://hoiquan.dpdns.org/VTVGo/?sctv19",
    "sctv21hd": "https://hoiquan.dpdns.org/VTVGo/?sctv21",
}

def fetch_live_link(url):
    try:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            content = response.read().decode('utf-8').strip()
            # Kiểm tra nếu nội dung trả về có dạng link http/https
            if content.startswith("http"):
                return content
            # Nếu web trả về cả cục m3u, tìm dòng http đầu tiên
            match = re.search(r'(https?://\S+)', content)
            if match:
                return match.group(1)
    except Exception as e:
        print(f"Lỗi khi lấy link từ {url}: {e}")
    return None

def main():
    m3u_file = "ghimtui.github.io/tivi.m3u"
    
    # Đọc nội dung file tivi.m3u hiện tại
    try:
        with open(m3u_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Không tìm thấy file {m3u_file} ở thư mục gốc!")
        return

    # Lấy link mới cho tất cả các kênh
    live_links = {}
    for tvg_id, url in CHANNELS.items():
        print(f"Đang lấy link cho {tvg_id}...")
        link = fetch_live_link(url)
        if link:
            live_links[tvg_id] = link
            print(f"-> Thành công: {link}")
        else:
            print(f"-> Thất bại!")

    # Cập nhật vào nội dung m3u
    new_lines = []
    skip_next = False
    
    for i, line in enumerate(lines):
        if skip_next:
            skip_next = False
            continue
            
        new_lines.append(line)
        
        # Nếu dòng hiện tại là #EXTINF, kiểm tra tvg-id
        if line.startswith("#EXTINF"):
            # Tìm tvg-id="..."
            match = re.search(r'tvg-id="([^"]+)"', line)
            if match:
                tvg_id = match.group(1)
                # Nếu tvg-id này có trong danh sách cần cập nhật và dòng tiếp theo là link cũ
                if tvg_id in live_links and i + 1 < len(lines):
                    next_line = lines[i+1].strip()
                    if next_line.startswith("http") or next_line == "":
                        new_lines.append(live_links[tvg_id] + "\n")
                        skip_next = True # Bỏ qua không add dòng link cũ nữa

    # Ghi lại vào file tivi.m3u tại thư mục gốc
    with open(m3u_file, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
    print("Đã cập nhật file tivi.m3u thành công!")

if __name__ == "__main__":
    main()
