#!/bin/bash
mkdir -p hls

# Thêm -re để đồng bộ, dùng -preset ultrafast để xử lý siêu nhanh
# Dùng -t 10 để tạo 1 phân đoạn mồi 10 giây rồi tắt, GitHub sẽ hoàn thành ngay lập tức
ffmpeg -re -loop 1 -i "http://baocamau.vn/live/radio_online.jpg" \
-i "http://live-hq.evgcdn.net/live/2851dd3d9016ac74d84b0c4a7a659f76891/chunklist.m3u8" \
-c:v libx264 -preset ultrafast -tune stillimage -pix_fmt yuv420p -b:v 50k -g 25 \
-c:a copy -t 10 \
-f hls -hls_time 5 -hls_list_size 2 -hls_playlist_type vvod hls/tay-ninh-radio.m3u8
