import re
import urllib.request

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
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8')
            # Tìm link định dạng .m3u8 trong mã nguồn trả về
            match = re.search(r'http[s]?://[^\s"\']+\.m3u8[^\s"\']*', html)
            if match:
                return match.group(0).strip()
    except Exception as e:
        print(f"Lỗi khi tải từ {url}: {e}")
    return None

def main():
    m3u_file = "tivi.m3u"
    
    # Đọc nội dung file tivi.m3u hiện tại
    try:
        with open(m3u_file, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Không tìm thấy file {m3u_file} ở thư mục gốc!")
        return

    # Duyệt qua từng kênh để lấy link mới và thay thế
    for channel_id, info in CHANNELS.items():
        new_link = get_live_link(info["url"])
        if new_link:
            # Dùng Regex để tìm link cũ tương ứng và thay bằng link mới
            content, count = re.subn(info["pattern"], new_link, content)
            if count > 0:
                print(f"[{channel_id.upper()}] Đã cập nhật thành công link mới.")
            else:
                print(f"[{channel_id.upper()}] Tìm thấy link mới nhưng không khớp cấu trúc để thay thế trong tivi.m3u.")
        else:
            print(f"[{channel_id.upper()}] Không lấy được link mới từ nguồn.")

    # Ghi đè lại nội dung mới vào file tivi.m3u
    with open(m3u_file, "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    main()
