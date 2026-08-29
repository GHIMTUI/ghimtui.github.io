import os
import re
import requests

# 1. Định nghĩa danh sách các kênh, hỗ trợ cấu trúc danh sách URL để fallback khi lỗi
CHANNELS = {
    "sctv2": {
        "url": [
"https://vmttv.dpdns.org/VTVGo/?sctv2",           "http://tv.vietanhtv.top/vieon/vieon.php?id=sctv2-57c3884d"],
        "tvg_id": "sctv2hd"
},
    "sctv3": {"url": ["https://vmttv.dpdns.org/VTVGo/?sctv3", 
"http://tv.vietanhtv.top/vieon/vieon.php?id=sctv3-hd-cf3adaca"], 
      "tvg_id": "sctv3hd"
 },
    "sctv4": {"url": ["https://vmttv.dpdns.org/VTVGo/?sctv4",
"http://tv.vietanhtv.top/vieon/vieon.php?id=sctv4-ae779f7e"
],
     "tvg_id": "sctv4hd"
   },
    "sctv7": {"url": ["https://vmttv.dpdns.org/VTVGo/?sctv7",
"http://tv.vietanhtv.top/vieon/vieon.php?id=sctv7-ef7e259a"], 
  "tvg_id": "sctv7hd"
  },
    "sctv9": {"url": ["https://vmttv.dpdns.org/VTVGo/?sctv9",
"http://tv.vietanhtv.top/vieon/vieon.php?id=sctv9-cdd19ab2"], 
  "tvg_id": "sctv9hd"
},
    "sctv11": {"url": ["https://vmttv.dpdns.org/VTVGo/?sctv11", 
"http://tv.vietanhtv.top/vieon/vieon.php?id=sctv11-1d565c47"], 
  "tvg_id": "sctv11hd"
},
    "sctv12": {"url": ["https://vmttv.dpdns.org/VTVGo/?sctv12", "http://tv.vietanhtv.top/vieon/vieon.php?id=sctv12-b0d6c023"], 
"tvg_id": "sctv12hd"
},
    "sctv13": {"url": ["https://vmttv.dpdns.org/VTVGo/?sctv13", "http://tv.vietanhtv.top/vieon/vieon.php?id=sctv13-67f88fcb"], 
"tvg_id": "sctv13hd"
},
    "sctv16": {"url": ["https://vmttv.dpdns.org/VTVGo/?sctv16", "http://tv.vietanhtv.top/vieon/vieon.php?id=sctv16-dd1535e8"], 
"tvg_id": "sctv16hd"
},
    "sctv18": {"url": ["https://vmttv.dpdns.org/VTVGo/?sctv18", "http://tv.vietanhtv.top/vieon/vieon.php?id=sctv18-398b0b4e"], 
"tvg_id": "sctv18hd"
},
    "sctv19": {"url": ["http://vietanhtv.id.vn/sctv/tv.php?id=sctv19-bf00bd02"], 
"tvg_id": "sctv19hd"
},
    "sctv21": {"url": ["http://vietanhtv.id.vn/sctv/tv.php?id=sctv-21-57de221a"], 
"tvg_id": "sctv21hd"
},
    "sctvphim": {"url": ["https://vmttv.dpdns.org/VTVGo/?sctvphim, "http://tv.vietanhtv.top/vieon/vieon.php?id=sctv-phim-tong-hop-e6d2df88"], 
"tvg_id": "sctvhdpth"
},
    "onviedramas": {"url": ["http://tv.vietanhtv.top/vieon/vieon.php?id=vie-dramas-hd"], 
"tvg_id": "onviedramas"
},
    "onviegiaitri": {"url": ["http://tv.vietanhtv.top/vieon/vieon.php?id=vie-giai-tri-hd"], 
"tvg_id": "onviegiaitri"
},
    "thanhhoa": {"url": ["http://tv.vietanhtv.top/vieon/vieon.php?id=thanh-hoa-48"], 
"tvg_id": "thanhhoa"
},
}

FAST_CHANNELS = [""]
FILE_NAME = "tivi.m3u"

def get_live_link(urls, channel_name):
    # Đảm bảo urls luôn là danh sách để lặp qua
    if isinstance(urls, str):
        urls = [urls]

    for idx, url in enumerate(urls, 1):
        try:
            print(f"[{channel_name.upper()}] Đang thử link {idx}: {url}")
            response = requests.get(url, timeout=15, allow_redirects=True)
            
            if response.status_code == 200:
                final_url = response.url
                
                # Logic thay đổi đuôi master.m3u8 thành playlist phù hợp
                if "master.m3u8" in final_url:
                    ch_name = channel_name.lower()
                    if ch_name == "sctvphim":
                        final_url = final_url.replace("master.m3u8", "playlist_1080p.m3u8")
                    elif ch_name != "sctv14":
                        final_url = final_url.replace("master.m3u8", "playlist_720p.m3u8")
                
                print(f"[{channel_name.upper()}] Thành công với link {idx}: {final_url}")
                return final_url
            else:
                print(f"[{channel_name.upper()}] Link {idx} trả về mã lỗi HTTP {response.status_code}")
        except Exception as e:
            print(f"[{channel_name.upper()}] Lỗi khi kết nối link {idx}: {e}")

    print(f"[{channel_name.upper()}] Tất cả các link dự phòng đều thất bại.")
    return None

def update_m3u_file():
    if not os.path.exists(FILE_NAME):
        print(f"Lỗi: Không tìm thấy file {FILE_NAME} trong thư mục để sửa đổi.")
        return

    update_type = os.getenv("UPDATE_TYPE", "all")
    print(f"Chế độ lọc kênh hoạt động: {update_type.upper()}")

    channels_to_update = {}
    for name, config in CHANNELS.items():
        if update_type == "fast":
            if name in FAST_CHANNELS:
                channels_to_update[name] = config
        elif update_type == "slow":
            if name not in FAST_CHANNELS:
                channels_to_update[name] = config
        else:
            channels_to_update[name] = config

    if not channels_to_update:
        print("Không có kênh nào cần cập nhật trong lượt này.")
        return

    with open(FILE_NAME, "r", encoding="utf-8") as f:
        content = f.read()

    has_changed = False

    for channel_name, config in channels_to_update.items():
        tvg_id = config["tvg_id"]
        source_urls = config["url"]
        
        new_link = get_live_link(source_urls, channel_name)
        if not new_link:
            continue

        pattern = rf'(#EXTINF:[^\n]*tvg-id="{tvg_id}"[^\n]*\n(?:#KODIPROP:[^\n]*\n)*)(https?://[^\n]+)'

        if re.search(pattern, content, re.IGNORECASE):
            content, count = re.subn(pattern, rf'\1{new_link}', content, flags=re.IGNORECASE)
            if count > 0:
                print(f"--> Đã cập nhật link {channel_name.upper()}")
                has_changed = True
        else:
            print(f"--> Cảnh báo: Không tìm thấy cấu trúc kênh {channel_name.upper()} với tvg-id=\"{tvg_id}\" trong m3u.")

    if has_changed:
        with open(FILE_NAME, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"\n Hoàn tất! Đã lưu các thay đổi vào {FILE_NAME}.")
    else:
        print("\n Không có thay đổi nào được thực hiện trên file.")

if __name__ == "__main__":
    update_m3u_file()
