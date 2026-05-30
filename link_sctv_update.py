import cloudscraper
import re

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

def fetch_live_link(scraper, url):
    try:
        # Thực hiện request giả lập trình duyệt vượt qua kiểm tra JavaScript của Cloudflare
        response = scraper.get(url, timeout=15)
        if response.status_code == 200:
            content = response.text.strip()
            # Tìm link http/https đầu tiên xuất hiện trong nội dung trả về
            match = re.search(r'(https?://\S+)', content)
            if match:
                return match.group(1).replace('"', '').replace("'", "").strip()
        else:
            print(f"-> Mã lỗi HTTP: {response.status_code}")
    except Exception as e:
        print(f"Lỗi khi cào link: {e}")
    return None

def main():
    m3u_file = "tivi.m3u"
    try:
        with open(m3u_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Không tìm thấy file {m3u_file} ở thư mục gốc!")
        return

    # Khởi tạo công cụ vượt Cloudflare (giả lập trình duyệt Chrome trên Windows)
    scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False})
    
    live_links = {}
    for tvg_id, url in CHANNELS.items():
        print(f"Đang xử lý kênh {tvg_id}...")
        link = fetch_live_link(scraper, url)
        if link:
            live_links[tvg_id] = link
            print(f"-> Lấy link thành công: {link}")
        else:
            print(f"-> Không lấy được link hợp lệ!")

    new_lines = []
    skip_next = False
    count_updated = 0
    
    for i, line in enumerate(lines):
        if skip_next:
            skip_next = False
            continue
        new_lines.append(line)
        if line.startswith("#EXTINF"):
            match = re.search(r'tvg-id="([^"]+)"', line)
            if match:
                tvg_id = match.group(1)
                if tvg_id in live_links and i + 1 < len(lines):
                    new_lines.append(live_links[tvg_id] + "\n")
                    skip_next = True
                    count_updated += 1

    with open(m3u_file, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
        
    print(f"\n--- HOÀN THÀNH QUY TRÌNH ---")
    print(f"Cập nhật thành công: {count_updated}/{len(CHANNELS)} kênh vào file gốc.")

if __name__ == "__main__":
    main()
