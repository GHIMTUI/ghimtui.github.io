import urllib.request
import re
import ssl

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
        # Bỏ qua xác thực SSL nếu web nguồn bị lỗi chứng chỉ
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        # Giả lập như trình duyệt thật
        req = urllib.request.Request(
            url, 
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': '*/*'
            }
        )
        with urllib.request.urlopen(req, context=ctx, timeout=15) as response:
            content = response.read().decode('utf-8').strip()
            
            # Tìm link http/https đầu tiên xuất hiện trong nội dung trả về
            match = re.search(r'(https?://\S+)', content)
            if match:
                # Làm sạch link nếu có dấu nháy hoặc ký tự lạ
                return match.group(1).replace('"', '').replace("'", "").strip()
    except Exception as e:
        print(f"Lỗi khi kết nối tới {url}: {e}")
    return None

def main():
    m3u_file = "tivi.m3u"
    
    try:
        with open(m3u_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Không tìm thấy file {m3u_file} ở thư mục gốc!")
        return

    live_links = {}
    for tvg_id, url in CHANNELS.items():
        print(f"Đang lấy link cho {tvg_id}...")
        link = fetch_live_link(url)
        if link:
            live_links[tvg_id] = link
            print(f"-> Lấy được link: {link}")
        else:
            print(f"-> Thất bại không lấy được link!")

    new_lines = []
    skip_next = False
    count_updated = 0
    
    for i, line in enumerate(lines):
        if skip_next:
            skip_next = False
            continue
            
        new_lines.append(line)
        
        if line.startswith("#EXTINF"):
            # Tìm chính xác tvg-id trong dòng
            match = re.search(r'tvg-id="([^"]+)"', line)
            if match:
                tvg_id = match.group(1)
                if tvg_id in live_links and i + 1 < len(lines):
                    new_lines.append(live_links[tvg_id] + "\n")
                    skip_next = True
                    count_updated += 1

    with open(m3u_file, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
    print(f"Đã cập nhật xong! Tổng số kênh đã thay link: {count_updated}/{len(CHANNELS)}")

if __name__ == "__main__":
    main()
