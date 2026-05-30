import urllib.request
import re
import ssl

# Cấu hình bỏ qua xác thực SSL nếu chứng chỉ của trang mẹ bị lỗi
ssl_context = ssl._create_unverified_context()

# 1. Danh sách các kênh và link mẹ
channels = {
    "sctvpth": "https://hoiquan.dpdns.org/VTVGo/?sctvphim",
    "sctv1": "https://hoiquan.dpdns.org/VTVGo/?sctv1",
    "sctv4": "https://hoiquan.dpdns.org/VTVGo/?sctv4",
    "sctv7": "http://hoiquan.dpdns.org/VTVGo/?sctv7",
    "sctv8": "https://hoiquan.dpdns.org/VTVGo/?sctv8",
    "sctv11": "https://hoiquan.dpdns.org/VTVGo/?sctv11",
    "sctv13": "https://hoiquan.dpdns.org/VTVGo/?sctv13",
    "sctv14": "https://hoiquan.dpdns.org/VTVGo/?sctv14",
    "sctv18": "https://hoiquan.dpdns.org/VTVGo/?sctv18",
    "sctv19": "https://hoiquan.dpdns.org/VTVGo/?sctv19",
    "sctv21": "https://hoiquan.dpdns.org/VTVGo/?sctv21"
}

# 2. Tạo Header "xịn" giả lập trình duyệt Chrome để không bị chặn
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'vi,en-US;q=0.9,en;q=0.8',
    'Referer': 'https://hoiquan.dpdns.org/',
    'Origin': 'https://hoiquan.dpdns.org'
}

links = {}

print("--- Bắt đầu lấy link gốc từ hoiquan.dpdns.org ---")

for ch, url in channels.items():
    try:
        req = urllib.request.Request(url, headers=headers)
        # Thực hiện gọi link mẹ
        with urllib.request.urlopen(req, context=ssl_context, timeout=15) as response:
            final_url = response.geturl()
            content = response.read().decode('utf-8', errors='ignore')
            
            # Cách 1: Nếu trang web redirect thẳng tới link m3u8
            if "m3u8" in final_url:
                links[ch] = final_url
                print(f"[Redirect] {ch} -> {final_url}")
            else:
                # Cách 2: Tìm link m3u8 ẩn bên trong mã nguồn (HTML/Javascript) của trang
                # Tìm tất cả các chuỗi bắt đầu bằng http... và kết thúc bằng .m3u8
                match = re.search(r'(https?://[^\s"\'\`>]+?\.m3u8[^\s"\'\`>]*)', content)
                if match:
                    raw_link = match.group(1)
                    # Xử lý nếu link bị dính dấu chống backslash (/) thường gặp trong javascript
                    raw_link = raw_link.replace('\\/', '/')
                    links[ch] = raw_link
                    print(f"[Tìm thấy trong Code] {ch} -> {raw_link}")
                else:
                    # Cách 3: Nếu không thấy m3u8, thử tìm link vtvdigital dạng thường
                    match_vtv = re.search(r'(https?://[^\s"\'\`>]+?vtvdigital\.vn[^\s"\'\`>]*)', content)
                    if match_vtv:
                        links[ch] = match_vtv.group(1).replace('\\/', '/')
                        print(f"[Tìm thấy dạng VTV] {ch} -> {links[ch]}")
                    else:
                        print(f"[Thất bại] {ch} không tìm thấy link m3u8 hợp lệ trong mã nguồn.")
                        links[ch] = "http://error-link-expired.m3u8"
                        
    except Exception as e:
        print(f"[Lỗi kết nối] {ch}: {e}")
        links[ch] = "http://error-connection-failed.m3u8"

# 3. Tiến hành ghi đè dữ liệu mới vào file playlist.m3u
m3u_content = f"""#EXTM3U
#EXTINF:-1 tvg-id="sctvhdpth" tvg-logo="https://raw.githubusercontent.com/PhatBee/phatbeetv/refs/heads/main/logo/SCTV/SCTVPTH.png",SCTV Phim Tổng Hợp
{links.get('sctvpth')}

#EXTINF:-1 tvg-id="sctv1hd" tvg-logo="https://raw.githubusercontent.com/PhatBee/phatbeetv/refs/heads/main/logo/SCTV/SCTV1.png",SCTV1
{links.get('sctv1')}

#EXTINF:-1 tvg-id="sctv4hd" tvg-logo="https://raw.githubusercontent.com/PhatBee/phatbeetv/refs/heads/main/logo/SCTV/SCTV4.png",SCTV4 
{links.get('sctv4')}

#EXTINF:-1 tvg-id="sctv7hd" tvg-logo="https://raw.githubusercontent.com/PhatBee/phatbeetv/refs/heads/main/logo/SCTV/SCTV7.png",SCTV7 
{links.get('sctv7')}

#EXTINF:-1 tvg-id="sctv8hd" tvg-logo="https://raw.githubusercontent.com/PhatBee/phatbeetv/refs/heads/main/logo/SCTV/SCTV8.png",SCTV8
{links.get('sctv8')}

#EXTINF:-1 tvg-id="sctv11hd" tvg-logo="https://raw.githubusercontent.com/PhatBee/phatbeetv/refs/heads/main/logo/SCTV/SCTV11.png",SCTV11
{links.get('sctv11')}

#EXTINF:-1 tvg-id="sctv13hd" tvg-logo="https://raw.githubusercontent.com/PhatBee/phatbeetv/refs/heads/main/logo/SCTV/SCTV13.png",SCTV13
{links.get('sctv13')}

#EXTINF:-1 tvg-id="sctv14hd" tvg-logo="https://raw.githubusercontent.com/PhatBee/phatbeetv/refs/heads/main/logo/SCTV/SCTV14.png",SCTV14 
{links.get('sctv14')}

#EXTINF:-1 tvg-id="sctv18hd" tvg-logo="https://raw.githubusercontent.com/PhatBee/phatbeetv/refs/heads/main/logo/SCTV/SCTV18.png",SCTV18 
{links.get('sctv18')}

#EXTINF:-1 tvg-id="sctv19hd" tvg-logo="https://raw.githubusercontent.com/PhatBee/phatbeetv/refs/heads/main/logo/SCTV/SCTV19.png",SCTV19
{links.get('sctv19')}

#EXTINF:-1 tvg-id="sctv21hd" tvg-logo="https://raw.githubusercontent.com/PhatBee/phatbeetv/refs/heads/main/logo/SCTV/SCTV21.png",SCTV21
{links.get('sctv21')}
"""

with open("tivi.m3u", "w", encoding="utf-8") as f:
    f.write(m3u_content)

print("--- Đã cập nhật xong file playlist.m3u ---")
