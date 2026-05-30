import urllib.request
import os

# Danh sách map giữa Tên kênh (trong file m3u) và Link API lấy token mới
CHANNELS_API = {
    "SCTV Phim Tổng Hợp": "https://hoiquan.dpdns.org/VTVGo/?sctvphim",
    "SCTV1": "https://hoiquan.dpdns.org/VTVGo/?sctv1",
    "SCTV4": "https://hoiquan.dpdns.org/VTVGo/?sctv4",
    "SCTV8": "https://hoiquan.dpdns.org/VTVGo/?sctv8",
    "SCTV11": "https://hoiquan.dpdns.org/VTVGo/?sctv11",
    "SCTV13": "https://hoiquan.dpdns.org/VTVGo/?sctv13",
    "SCTV14": "https://hoiquan.dpdns.org/VTVGo/?sctv14",
    "SCTV18": "https://hoiquan.dpdns.org/VTVGo/?sctv18",
    "SCTV19": "https://hoiquan.dpdns.org/VTVGo/?sctv19",
    "SCTV21": "https://hoiquan.dpdns.org/VTVGo/?sctv21"
}

def get_new_m3u8(api_url):
    """Gọi API để lấy link m3u8 mới với header giả lập trình duyệt Chrome"""
    # Ngụy trang thành trình duyệt Chrome thật trên Windows
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
        'Referer': 'https://hoiquan.dpdns.org/',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    try:
        req = urllib.request.Request(api_url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            content = response.read().decode('utf-8').strip()
            # Nếu API trả về trực tiếp đoạn text chứa link
            if content.startswith("http"):
                return content
            # Nếu API sử dụng redirect (chuyển hướng) thẳng tới link m3u8
            elif response.geturl() != api_url:
                return response.geturl()
    except Exception as e:
        print(f"Lỗi khi lấy link {api_url}: {e}")
    return None

def update_m3u_file(filepath="tivi.m3u"):
    if not os.path.exists(filepath):
        print(f"Không tìm thấy file {filepath}")
        return

    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    updated = False
    for i in range(len(lines)):
        if lines[i].startswith("#EXTINF"):
            for channel_name, api_url in CHANNELS_API.items():
                if f",{channel_name}" in lines[i]:
                    new_link = get_new_m3u8(api_url)
                    if new_link and (i + 1 < len(lines)) and lines[i+1].startswith("http"):
                        if lines[i+1].strip() != new_link:
                            lines[i+1] = new_link + "\n"
                            print(f"Đã cập nhật thành công: {channel_name}")
                            updated = True
                        else:
                            print(f"Link chưa thay đổi, bỏ qua: {channel_name}")
                    break

    if updated:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print("Đã lưu các thay đổi vào tivi.m3u")
    else:
        print("Không có link nào cần cập nhật.")

if __name__ == "__main__":
    update_m3u_file()
