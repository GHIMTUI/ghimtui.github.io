import re
import urllib.request
import urllib.error

# Định nghĩa danh sách các link lấy token mới và định dạng nhận diện trong file m3u
CHANNELS = {
    "sctvphim": {
        "url": "http://hoiquan.dpdns.org/VTVGo/?sctvphim",
        "pattern": r"(http://vtvgolive-sctvdrm\.vtvdigital\.vn/[^/]+/[^/]+/manifest/sctvpth/[^\s]+)"
    },
    "sctv1": {
        "url": "http://hoiquan.dpdns.org/VTVGo/?sctv1",
        "pattern": r"(http://vtvgolive-sctv\.vtvdigital\.vn/[^/]+/[^/]+/asdfasdvgas2vtvsctv/1/[^\s]+)"
    },
    "sctv4": {
        "url": "http://hoiquan.dpdns.org/VTVGo/?sctv4",
        "pattern": r"(http://vtvgolive-sctvdrm\.vtvdigital\.vn/[^/]+/[^/]+/manifest/sctv4/[^\s]+)"
    },
    "sctv8": {
        "url": "http://hoiquan.dpdns.org/VTVGo/?sctv8",
        "pattern": r"(http://vtvgolive-sctv\.vtvdigital\.vn/[^/]+/[^/]+/bdnc6qbiq1vtvsctv/8/[^\s]+)"
    },
    "sctv11": {
        "url": "http://hoiquan.dpdns.org/VTVGo/?sctv11",
        "pattern": r"(http://vtvgolive-sctvdrm\.vtvdigital\.vn/[^/]+/[^/]+/manifest/sctv11/master\.[^\s]+)"
    },
    "sctv13": {
        "url": "http://hoiquan.dpdns.org/VTVGo/?sctv13",
        "pattern": r"(http://vtvgolive-sctvdrm\.vtvdigital\.vn/[^/]+/[^/]+/manifest/sctv11/playlist_720p\.[^\s]+)"
    },
    "sctv14": {
        "url": "http://hoiquan.dpdns.org/VTVGo/?sctv14",
        "pattern": r"(http://vtvgolive-sctv\.vtvdigital\.vn/[^/]+/[^/]+/6GoYKNrTy3vtvsctv/14/[^\s]+)"
    },
    "sctv18": {
        "url": "http://hoiquan.dpdns.org/VTVGo/?sctv18",
        "pattern": r"(http://vtvgolive-sctvdrm\.vtvdigital\.vn/[^/]+/[^/]+/manifest/sctv18/[^\s]+)"
    },
    "sctv19": {
        "url": "http://hoiquan.dpdns.org/VTVGo/?sctv19",
        "pattern": r"(http://vtvgolive-sctv\.vtvdigital\.vn/[^/]+/[^/]+/5m63a995d8vtvsctv/19/[^\s]+)"
    },
    "sctv21": {
        "url": "http://hoiquan.dpdns.org/VTVGo/?sctv21",
        "pattern": r"(http://vtvgolive-sctv\.vtvdigital\.vn/[^/]+/[^/]+/bdnc6qbiq1vtvsctv/21/[^\s]+)"
    }
}

def get_live_link(url):
    # Tạo bộ headers "xịn" giả lập trình duyệt Chrome đầy đủ thông tin để vượt tường lửa
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'vi,en-US;q=0.9,en;q=0.8',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            html = response.read().decode('utf-8')
            # Tìm link .m3u8 xuất hiện trong mã nguồn
            match = re.search(r'http[s]?://[^\s"\']+\.m3u8[^\s"\']*', html)
            if match:
                return match.group(0).strip()
    except urllib.error.HTTPError as e:
        print(f"Lỗi HTTP {e.code} khi tải từ {url}")
    except urllib.error.URLError as e:
        print(f"Lỗi kết nối mạng: {e.reason} tại {url}")
    except Exception as e:
        print(f"Lỗi hệ thống không xác định: {e} tại {url}")
    return None

def main():
    m3u_file = "tivi.m3u"
    
    try:
        with open(m3u_file, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Không tìm thấy file {m3u_file} ở thư mục gốc!")
        return

    for channel_id, info in CHANNELS.items():
        new_link = get_live_link(info["url"])
        if new_link:
            content, count = re.subn(info["pattern"], new_link, content)
            if count > 0:
                print(f"[{channel_id.upper()}] Cập nhật thành công.")
            else:
                print(f"[{channel_id.upper()}] Lấy được link mới nhưng cấu trúc regex không khớp với link cũ trong file m3u.")
        else:
            print(f"[{channel_id.upper()}] Thất bại: Không phản hồi hoặc bị chặn.")

    with open(m3u_file, "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    main()
