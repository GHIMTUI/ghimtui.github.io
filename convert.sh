#!/bin/bash

# Tạo thư mục chứa file xuất ra
mkdir -p hls

# Chạy FFmpeg để trộn ảnh tĩnh và link radio thành luồng video HLS (.m3u8)
ffmpeg -loop 1 -i "http://baocamau.vn/live/radio_online.jpg" \
-i "http://live-hq.evgcdn.net/live/2851dd3d9016ac74d84b0c4a7a659f76891/chunklist.m3u8" \
-c:v libx264 -tune stillimage -pix_fmt yuv420p -b:v 150k -g 50 \
-c:a copy -shortest \
-f hls -hls_time 6 -hls_playlist_type event hls/tayninh-radio.m3u8
