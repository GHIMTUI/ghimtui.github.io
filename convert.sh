#!/bin/bash
mkdir -p hls

# Cấu hình FFmpeg sửa lỗi không ghi được header
ffmpeg -loop 1 -i "http://baocamau.vn/live/radio_online.jpg" \
-i "http://live-hq.evgcdn.net/live/2851dd3d9016ac74d84b0c4a7a659f76891/chunklist.m3u8" \
-map 0:v:0 -map 1:a:0 \
-c:v libx264 -preset ultrafast -tune stillimage -pix_fmt yuv420p -b:v 50k -g 25 \
-c:a aac -b:a 64k -t 10 \
-f hls -hls_time 5 -hls_list_size 2 -hls_playlist_type vod hls/tay-ninh-radio.m3u8
