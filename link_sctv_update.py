import urllib.request
import re

# 1. Định nghĩa danh sách các kênh và link mẹ tương ứng
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

# Giả lập Header để tránh bị chặn (User-Agent)
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

links = {}

# 2. Cào (Get) link gốc từ link mẹ
for ch, url in channels.items():
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            # Nếu link mẹ tự redirect thẳng sang link m3u8
            final_url = response.geturl()
            
            # Nếu không redirect mà trả về nội dung text chứa link, ta dùng Regex để tìm
            if "m3u8" not in final_url:
                content = response.read().decode('utf-8', errors='ignore')
                match = re.search(r'(https?://[^\s"\']+\.m3u8[^\s"\']*)', content)
                if match:
                    final_url = match.group(1)
            
            links[ch] = final_url
            print(f"Thành công {ch}: {final_url}")
    except Exception as e:
        print(f"Lỗi khi lấy link {ch}: {e}")
        # Nếu lỗi, giữ một link tạm thời hoặc bỏ trống
        links[ch] = "http://error-or-expired-link.m3u8"

# 3. Tạo nội dung file M3U mới
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

# 4. Ghi nội dung ra file playlist.m3u
with open("tivi.m3u", "w", encoding="utf-8") as f:
    f.write(m3u_content)
