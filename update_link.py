import os
import re
import requests

# Cấu hình file mục tiêu và URL nguồn
SOURCE_URL = "http://vmttv.dpdns.org/VTVGo/?sctv14"
FILE_NAME = "tivi.m3u"

def get_live_link():
    try:
        # Gửi request và đi theo redirect để lấy link .m3u8 thực tế mới nhất
        response = requests.get(SOURCE_URL, timeout=15, allow_redirects=True)
        final_url = response.url
        print(f"Đã lấy được link mới nhất: {final_url}")
        return final_url
    except Exception as e:
        print(f"Lỗi khi kết nối lấy link từ nguồn: {e}")
        return None

def update_m3u_file(new_link):
    if not new_link:
        print("Không có link mới, hủy cập nhật.")
        return

    if not os.path.exists(FILE_NAME):
        print(f"Lỗi: Không tìm thấy file {FILE_NAME} trong kho lưu trữ để sửa đổi.")
        return

    # Đọc toàn bộ nội dung hiện tại của file tivi.m3u
    with open(FILE_NAME, "r", encoding="utf-8") as f:
        content = f.read()

    # Định nghĩa biểu thức chính quy (Regex) để tìm chính xác cụm của SCTV14
    # Tìm từ dòng #EXTINF có chứa tvg-id="sctv14hd" cho đến hết các dòng #KODIPROP (nếu có)
    # và bắt lấy dòng URL http/https nằm ở cuối cụm đó.
    pattern = r'(#EXTINF:[^\n]*tvg-id="sctv14hd"[^\n]*\n(?:#KODIPROP:[^\n]*\n)*)(http?://[^\n]+)'

    # Kiểm tra xem cấu trúc kênh SCTV14 có tồn tại trong file hay không
    if not re.search(pattern, content, re.IGNORECASE):
        print("Cảnh báo: Không tìm thấy kênh SCTV14 với tvg-id=\"sctv14hd\" trong file tivi.m3u.")
        return

    # Tiến hành thay thế: giữ nguyên cụm thẻ cấu hình (\1), chỉ đổi phần URL thành link mới
    updated_content = re.sub(pattern, rf'\1{new_link}', content, flags=re.IGNORECASE)

    # Ghi đè nội dung đã cập nhật trở lại file tivi.m3u
    with open(FILE_NAME, "w", encoding="utf-8") as f:
        f.write(updated_content)
    print(f"Đã cập nhật thành công link mới cho kênh SCTV14 trong file {FILE_NAME}!")

if __name__ == "__main__":
    link = get_live_link()
    update_m3u_file(link)
