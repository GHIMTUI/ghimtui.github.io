import os
import cloudscraper

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
    """Sử dụng cloudscraper để vượt tường lửa chống bot (Cloudflare/WAF)"""
    # Khởi tạo scraper ngụy trang thành Chrome trên Windows
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        }
    )
    
    try:
        response = scraper.get(api_url, timeout=15)
        
        # Nếu trang trả về mã 200 (Thành công)
        if response.status_code == 200:
            content = response.text.strip()
            # Nếu nội dung trả về là 1 link m3u8 trực tiếp
            if content.startswith("http"):
                return content
                
        # Nếu web sử dụng cơ chế chuyển hướng (Redirect)
        if response.url != api_url and response.url.startswith("http"):
            return response.url
            
    except Exception as e:
        print(f"Lỗi khi lấy link {api_url}: {e}")
        
    return None

def step1_fetch_and_save_txt():
    """BƯỚC 1: Lấy link mới và in ra thư mục file/link_sctv_update.txt"""
    os.makedirs(os.path.dirname(TXT_FILE_PATH), exist_ok=True)
    fetched_links = {}
    print("--- BƯỚC 1: Lấy link và lưu ra file txt ---")
    
    with open(TXT_FILE_PATH, 'w', encoding='utf-8') as f:
        for channel, api in CHANNELS_API.items():
            new_link = get_new_m3u8(api)
            if new_link:
                f.write(f"{channel}|{new_link}\n")
                fetched_links[channel] = new_link
                print(f"[+] Thành công: {channel}")
            else:
                print(f"[-] Thất bại: {channel}")
                
    return fetched_links

def step2_update_m3u(fetched_links):
    """BƯỚC 2: Cập nhật ngược lại vào tivi.m3u"""
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
                if f",{channel_name}" in lines[i]:
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
    links = step1_fetch_and_save_txt()
    if links:
        step2_update_m3u(links)
    else:
        print("Không có link nào được tải về, bỏ qua cập nhật tivi.m3u.")
