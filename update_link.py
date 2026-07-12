import os
import requests

# URL nguồn cần lấy
SOURCE_URL = "http://vmttv.dpdns.org/VTVGo/?sctv14"
FILE_NAME = "channel-tivi.txt"

def get_live_link():
    try:
        # Gửi request và tự động đi theo các bước redirect để lấy link .m3u8 cuối cùng
        response = requests.get(SOURCE_URL, timeout=15, allow_redirects=True)
        final_url = response.url
        print(f"Đã lấy được link gốc mới nhất: {final_url}")
        return final_url
    except Exception as e:
        print(f"Lỗi khi kết nối lấy link: {e}")
        return None

def update_file(new_link):
    if not new_link:
        return
        
    # Định dạng nội dung (Có thể tùy biến theo chuẩn playlist M3U nếu bạn muốn)
    line_to_write = f"#EXTINF:-1,SCTV 14\n{new_link}\n"
    
    # Ghi đè hoặc tạo mới file channel-tivi.txt
    with open(FILE_NAME, "w", encoding="utf-8") as f:
        f.write(line_to_write)
    print(f"Đã cập nhật link vào {FILE_NAME}")

if __name__ == "__main__":
    link = get_live_link()
    update_file(link)
