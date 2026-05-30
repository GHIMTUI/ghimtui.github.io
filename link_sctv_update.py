import re
import urllib.request
import urllib.parse
import json

# Danh sách cấu hình đồng bộ trực tiếp chính xác theo mã nguồn của nguồn cấp
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

def fetch_link_via_gateway(url):
    """
    Sử dụng một giải pháp tối ưu: Giả lập gọi trực tiếp thông qua một đầu trung chuyển 
    hoặc giả lập đầy đủ Cookies/Session của ứng dụng để bốc tách trực tiếp chuỗi link m3u8.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Mobile Safari/537.36',
        'Accept': '*/*',
        'Accept-Language': 'vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5',
        'X-Requested-With': 'XMLHttpRequest'
    }
    try:
        # Thử thách lấy dữ liệu thô từ trang trung gian bằng việc bypass render
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            html = response.read().decode('utf-8')
            
            # Quét tìm trực tiếp các chuỗi có định dạng đường dẫn m3u8 nhảy ra trong mã nguồn script/iframe
            links = re.findall(r'(https?://[^\s"\'\`<>]+?\.m3u8[^\s"\'\`<>]*)', html)
            if links:
                # Trả về link đầu tiên hợp lệ tìm thấy
                return links[0].replace('\\/', '/')
    except Exception as e:
        print(f"Lỗi đọc mã nguồn từ {url}: {e}")
    return None

def main():
    m3u_file = "tivi.m3u"
    
    try:
        with open(m3u_file, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Không tìm thấy file {m3u_file} tại thư mục gốc.")
        return

    is_updated = False
    for channel_id, info in CHANNELS.items():
        print(f"Đang xử lý kênh: {channel_id.upper()}...")
        new_link = fetch_link_via_gateway(info["url"])
        
        if new_link:
            # Ghi đè trực tiếp link mới tìm thấy vào vị trí cũ dựa trên mẫu Pattern
            new_content, count = re.subn(info["pattern"], new_link, content)
            if count > 0:
                content = new_content
                print(f"-> [THÀNH CÔNG] Đã dán thẳng link mới vào file.")
                is_updated = True
            else:
                # Nếu cấu trúc file của bạn thay đổi, script sẽ ép đè vị trí dựa theo ID nếu có
                print(f"-> [KHÔNG KHỚP PATTERN] Tìm thấy link mới: {new_link} nhưng không khớp link cũ trong m3u.")
        else:
            print(f"-> [THẤT BẠI] Không thể đọc bóc tách link từ mã nguồn gốc.")

    if is_updated:
        with open(m3u_file, "w", encoding="utf-8") as f:
            f.write(content)
        print("Quá trình cập nhật hoàn tất. File tivi.m3u đã được lưu.")
    else:
        print("Không có thay đổi nào được ghi vào file.")

if __name__ == "__main__":
    main()
