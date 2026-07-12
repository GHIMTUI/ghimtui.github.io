import os
import re
import requests

# 1. Định nghĩa danh sách các kênh cần lấy và mã tvg-id tương ứng trong file m3u
# Bạn có thể kiểm tra xem tvg-id trong file tivi.m3u của bạn đã khớp với các mã dưới đây chưa nhé.
CHANNELS = {
    "sctv3": {"url": "http://vmttv.dpdns.org/VTVGo/?sctv3", "tvg_id": "sctv3hd"},
    "sctv4": {"url": "http://vmttv.dpdns.org/VTVGo/?sctv4", "tvg_id": "sctv4hd"},
    "sctv7": {"url": "http://vmttv.dpdns.org/VTVGo/?sctv7", "tvg_id": "sctv7hd"},
    "sctv9": {"url": "http://vmttv.dpdns.org/VTVGo/?sctv9", "tvg_id": "sctv9hd"},
    "sctv11": {"url": "http://vmttv.dpdns.org/VTVGo/?sctv11", "tvg_id": "sctv11hd"},
    "sctv12": {"url": "http://vmttv.dpdns.org/VTVGo/?sctv12", "tvg_id": "sctv12hd"},
    "sctv13": {"url": "http://vmttv.dpdns.org/VTVGo/?sctv13", "tvg_id": "sctv13hd"},
    "sctv14": {"url": "http://vmttv.dpdns.org/VTVGo/?sctv14", "tvg_id": "sctv14hd"},
    "sctv18": {"url": "http://vmttv.dpdns.org/VTVGo/?sctv18", "tvg_id": "sctv18hd"},
    "sctv19": {"url": "http://vmttv.dpdns.org/VTVGo/?sctv19", "tvg_id": "sctv19hd"},
    "sctv21": {"url": "http://vmttv.dpdns.org/VTVGo/?sctv21", "tvg_id": "sctv21hd"},
    "sctvphim": {"url": "http://vmttv.dpdns.org/VTVGo/?sctvphim", "tvg_id": "sctvhdpth"},
}

FILE_NAME = "tivi.m3u"

def get_live_link(url, channel_name):
    try:
        # Gửi request và đi theo redirect để lấy link .m3u8 thực tế mới nhất
        response = requests.get(url, timeout=15, allow_redirects=True)
        final_url = response.url
        print(f"[{channel_name.upper()}] Đã lấy được link mới nhất: {final_url}")
        return final_url
    except Exception as e:
        print(f"[{channel_name.upper()}] Lỗi khi kết nối lấy link: {e}")
        return None

def update_m3u_file():
    if not os.path.exists(FILE_NAME):
        print(f"Lỗi: Không tìm thấy file {FILE_NAME} trong thư mục để sửa đổi.")
        return

    # Đọc toàn bộ nội dung hiện tại của file tivi.m3u một lần duy nhất
    with open(FILE_NAME, "r", encoding="utf-8") as f:
        content = f.read()

    has_changed = False

    # Duyệt qua từng kênh để tìm và thay thế link
    for channel_name, config in CHANNELS.items():
        tvg_id = config["tvg_id"]
        source_url = config["url"]
        
        # Lấy link stream mới của kênh hiện tại
        new_link = get_live_link(source_url, channel_name)
        if not new_link:
            continue

        # Tạo biểu thức chính quy (Regex) động cho từng mã tvg-id cụ thể
        # Tìm từ dòng #EXTINF có chứa tvg-id="..." chính xác cho đến hết các dòng #KODIPROP và URL cũ
        pattern = rf'(#EXTINF:[^\n]*tvg-id="{tvg_id}"[^\n]*\n(?:#KODIPROP:[^\n]*\n)*)(http?://[^\n]+)'

        # Kiểm tra xem kênh có trong file không
        if re.search(pattern, content, re.IGNORECASE):
            # Tiến hành thay thế link cho kênh này
            content, count = re.subn(pattern, rf'\1{new_link}', content, flags=re.IGNORECASE)
            if count > 0:
                print(f"--> Đã cập nhật thành công link cho {channel_name.upper()}")
                has_changed = True
        else:
            print(f"--> Cảnh báo: Không tìm thấy cấu trúc kênh {channel_name.upper()} với tvg-id=\"{tvg_id}\" trong m3u.")

    # Nếu có bất kỳ kênh nào được thay đổi link, thực hiện ghi đè lại file
    if has_changed:
        with open(FILE_NAME, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"\n Hoàn tất! Đã cập nhật xong toàn bộ các kênh được tìm thấy trong {FILE_NAME}.")
    else:
        print("\n Không có kênh nào thay đổi link hoặc không tìm thấy kênh phù hợp để cập nhật.")

if __name__ == "__main__":
    update_m3u_file()
