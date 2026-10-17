import re
import requests
from channels import CHANNELS

M3U_FILE = "tivi.m3u"


def check_url_active(url):
  """Kiểm tra link stream có phản hồi status code 200 hay không."""
  try:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    response = requests.get(url, headers=headers, timeout=5, stream=True)
    if response.status_code == 200:
      return True
  except Exception:
    pass
  return False


def get_working_url(url_list):
  """Lọc ra các link có cấu hình "getlink": True để kiểm tra.

  Nếu tất cả các link getlink đều lỗi, trả về link đầu tiên trong danh sách.
  """
  urls_to_check = []

  # Duyệt qua danh sách URL để tìm những phần tử có "getlink": True
  for item in url_list:
    if isinstance(item, dict) and item.get("getlink") is True:
      urls_to_check.append(item.get("url"))

  # Tiến hành get/check các link được chỉ định
  for url in urls_to_check:
    print(f"Đang kiểm tra (getlink): {url}")
    if check_url_active(url):
      print(f"-> Link hoạt động tốt: {url}")
      return url

  print("-> Không có link getlink nào hoạt động (hoặc tất cả đều lỗi)!")

  # Trả về link đầu tiên (lấy string nếu là dict) để tránh rỗng
  first_item = url_list[0]
  if isinstance(first_item, dict):
    return first_item.get("url")
  return first_item


def update_m3u_file():
  try:
    with open(M3U_FILE, "r", encoding="utf-8") as f:
      content = f.read()
  except FileNotFoundError:
    print(f"Không tìm thấy file {M3U_FILE}")
    return

  updated = False

  for key, data in CHANNELS.items():
    url_list = data.get("url", [])
    tvg_id = data.get("tvg_id")

    if not url_list or not tvg_id:
      continue

    best_url = get_working_url(url_list)

    # Tìm chính xác vị trí kênh dựa trên tvg-id trong file M3U
    pattern = rf'(#EXTINF:[^\n]*tvg-id="{tvg_id}"[^\n]*\n)([^\n]+)'

    match = re.search(pattern, content)
    if match:
      old_url = match.group(2).strip()
      if old_url != best_url:
        content = content.replace(old_url, best_url)
        print(f"Đã cập nhật link mới cho tvg_id '{tvg_id}': {best_url}")
        updated = True
      else:
        print(f"Kênh tvg_id '{tvg_id}' không cần thay đổi link.")
    else:
      print(f"Không tìm thấy kênh có tvg_id='{tvg_id}' trong file {M3U_FILE}.")

  if updated:
    with open(M3U_FILE, "w", encoding="utf-8") as f:
      f.write(content)
    print(f"Đã lưu thành công vào {M3U_FILE}")
  else:
    print("Không có cập nhật mới.")


if __name__ == "__main__":
  update_m3u_file()
