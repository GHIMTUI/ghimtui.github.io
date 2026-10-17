import re
from channels import CHANNELS

def update_m3u_file(m3u_path="tivi.m3u"):
    try:
        with open(m3u_path, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Không tìm thấy file {m3u_path}")
        return

    for channel_key, data in CHANNELS.items():
        tvg_id = data["tvg_id"]
        new_urls = data["url"]
        
        # Nếu có nhiều URL, ưu tiên lấy URL đầu tiên hoặc tạo logic xoay vòng/kiểm tra sống chết tùy ý
        new_url = new_urls[0] if isinstance(new_urls, list) and new_urls else new_urls

        # Biểu thức chính quy tìm đến dòng định nghĩa kênh có tvg-id khớp và thay thế URL dòng tiếp theo
        # Ví dụ định dạng m3u phổ biến: #EXTINF:-1 tvg-id="sctv2hd",SCTV2\nLINK_STREAM
        pattern = re.compile(rf'(#EXTINF:[^\n]*tvg-id="{tvg_id}"[^\n]*\n)([^\n#]+)', re.IGNORECASE)
        
        if pattern.search(content):
            content = pattern.sub(rf'\1{new_url}', content)
            print(f"Đã cập nhật thành công link cho: {tvg_id}")
        else:
            print(f"Không tìm thấy tvg-id=\"{tvg_id}\" trong file m3u.")

    with open(m3u_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Đã lưu lại file tivi.m3u thành công.")

if __name__ == "__main__":
    update_m3u_file()
