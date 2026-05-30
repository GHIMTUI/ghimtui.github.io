import subprocess
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

def fetch_live_link(url):
    try:
        # Sử dụng lệnh curl_chrome116 (giả lập y hệt Chrome thật từ nhân mạng)
        cmd = [
            'curl_chrome116', '-s', '-L', '--max-time', '15',
            url
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8', errors='ignore')
        content = result.stdout.strip()
        
        if content:
            # Nếu Cloudflare trả về trang lỗi hoặc landing challenge, bỏ qua luôn
            if "cloudflare" in content.lower() and "error" in content.lower():
                return None
                
            match = re.search(r'(https?://\S+)', content)
            if match:
                return match.group(1).replace('"', '').replace("'", "").strip()
    except Exception as e:
        print(f"Lỗi hệ thống lệnh: {e}")
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
        print(f"Đang cào link cho {tvg_id}...")
        link = fetch_live_link(url)
        if link:
            live_links[tvg_id] = link
            print(f"-> Thành công lấy được: {link}")
        else:
            print(f"-> Thất bại (Bị Cloudflare chặn)")

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
    print(f"--- KẾT QUẢ CẬP NHẬT ---")
    print(f"Đã thay thế thành công: {count_updated}/{len(CHANNELS)} kênh.")

if __name__ == "__main__":
    main()
