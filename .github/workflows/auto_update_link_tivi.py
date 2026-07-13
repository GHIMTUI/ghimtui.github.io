import os
import re
import requests

# 1. Định nghĩa danh sách các kênh cần lấy và mã tvg-id tương ứng trong file m3u
CHANNELS = {
    "sctv3": {"url": "http://vmttv.dpdns.org/VTVGo/?sctv3", "tvg_id": "sctv3hd"},
    "sctv4": {"url": "http://vmttv.dpdns.org/VTVGo/?sctv4", "tvg_id": "sctv4hd"},
    "sctv7": {"url": "http://vmttv.dpdns.org/VTVGo/?sctv7", "tvg_id": "sctv7hd"},
    "sctv8": {"url": "http://vmttv.dpdns.org/VTVGo/?sctv8", "tvg_id": "sctv8hd"},
    "sctv9": {"url": "http://vmttv.dpdns.org/VTVGo/?sctv9", "tvg_id": "sctv9hd"},
    "sctv11": {"url": "http://vmttv.dpdns.org/VTVGo/?sctv11", "tvg_id": "sctv11hd"},
    "sctv12": {"url": "http://vmttv.dpdns.org/VTVGo/?sctv12", "tvg_id": "sctv12hd"},
    "sctv13": {"url": "http://vmttv.dpdns.org/VTVGo/?sctv13", "tvg_id": "sctv13hd"},
    "sctv14": {"url": "http://vmttv.dpdns.org/VTVGo/?sctv14", "tvg_id": "sctv14hd"},
    "sctv18": {"url": "http://vmttv.dpdns.org/VTVGo/?sctv18", "tvg_id": "sctv18hd"},
    "sctv19": {"url": "http://vmttv.dpdns.org/VTVGo/?sctv19", "tvg_id": "sctv19hd"},
    "sctv21": {"url": "http://vmttv.dpdns.org/VTVGo/?sctv21", "tvg_id": "sctv21hd"},
    "sctvphim": {"url": "http://vmttv.dpdns.org/VTVGo/?sctvphim", "tvg_id": "sctvphimhd"},
}

FILE_NAME = "tivi.m3u"

def get_live_link(url, channel_name):
    try:
        # Gửi request và đi theo redirect để lấy link thực tế mới nhất
        response = requests.get(url, timeout=20, allow_redirects=True)
        final_url = response.url
        
        # Bắt buộc chuyển đổi đầu link https thành http
        if final_url.startswith("https://"):
            final_url = final_url.replace("https://", "http://", 1)
            
        print(f"[{channel_name.upper()}] Đã lấy được link (HTTP): {final_url}")
        return final_url
    except Exception as e:
