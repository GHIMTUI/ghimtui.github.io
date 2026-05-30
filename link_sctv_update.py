import urllib.request
import os

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

TXT_FILE_PATH = "file/link_sctv_update.txt"
M3U_FILE_PATH = "tivi.m3u"

def get_new_m3u8(api_url):
    """Giả lập trình duyệt để vượt qua lỗi 403 Forbidden"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
        'Referer': 'https://hoiquan.dpdns.org/',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    try:
        req = urllib.request.Request(api_url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            content = response.read().decode('utf-8').strip()
            if content.startswith("http"):
                return content
            elif response.geturl() != api_url:
                return response.geturl()
    except Exception as e:
        print(f"Lỗi khi lấy link {api_url}: {e}")
    return None

def step1_fetch_and_save_txt():
    """BƯỚC 1: Lấy link mới và in ra thư mục file/link_sctv_update.txt"""
    # Tự động tạo thư mục 'file' nếu chưa có
    os.makedirs(os.path.dirname(TXT_FILE_PATH), exist_ok=True)
    
    fetched_links = {}
    print("--- BƯỚC 1: Lấy link và lưu ra file txt ---")
    
    with open(TXT_FILE_PATH, 'w', encoding='utf-8') as f:
        for channel, api in CHANNELS_API.items():
            new_link = get_new_m3u8(api)
            if new_link:
                # Lưu vào txt theo cấu trúc: Tên kênh|Link
                f.write(f"{channel}|{new_link}\n")
                fetched_links[channel] = new_link
                print(f"[+] Thành công: {channel}")
            else:
                print(f"[-] Thất bại: {channel}")
                
    return fetched_links

def step2_update_m3u(fetched_links):
    """BƯỚC 2: Cập nhật ngược lại vào tivi.m3u từ dữ liệu vừa lấy"""
    print("\n--- BƯỚC 2: Cập nhật tivi.m3u ---")
    if not os.path.exists(M3U_FILE_PATH):
        print(f"Không tìm thấy file {M3U_FILE_PATH}")
        return

    with open(M3U_FILE_PATH, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    updated = False
    for i in range(len(lines)):
        if lines[i].startswith("#EXTINF"):
            for channel_name, new_link in fetched_links.items():
                # Tìm dòng có chứa đúng tên kênh (có dấu phẩy ở trước)
                if f",{channel_name}" in lines[i]:
                    # Nếu dòng ngay bên dưới là link cũ thì đè link mới vào
                    if (i + 1 < len(lines)) and lines[i+1].startswith("http"):
                        if lines[i+1].strip() != new_link:
                            lines[i+1] = new_link + "\n"
                            print(f"Đã thay link mới cho: {channel_name}")
                            updated = True
                        else:
                            print(f"Link không đổi, giữ nguyên: {channel_name}")
                    break

    if updated:
        with open(M3U_FILE_PATH, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print(f"\n=> Đã lưu file {M3U_FILE_PATH} thành công!")
    else:
        print("\n=> Không có thay đổi nào để lưu.")

if __name__ == "__main__":
    # Chạy nối tiếp 2 bước
    links = step1_fetch_and_save_txt()
    if links:
        step2_update_m3u(links)
    else:
        print("Không có link nào được tải về, bỏ qua cập nhật tivi.m3u.")
