<?php
// 1. Khai báo định dạng đầu ra là video MPEG-TS để đầu phát IPTV nhận diện được
header("Content-Type: video/mp4");
header("Cache-Control: no-cache, must-revalidate");

// 2. Đường dẫn ảnh nền và đường dẫn luồng âm thanh Radio của bạn
$image_url = "https://media.baotayninh.vn/upload/channel/2d07bdc676fe7d422bda35e1f5170c47.jpg";
$audio_url = "http://live-hq.evgcdn.net/live/2851dd3d9016ac74d84b0c4a7a659f76891/chunklist.m3u8";

// 3. Câu lệnh FFmpeg để lặp lại ảnh nền và trộn với âm thanh
// -loop 1: Lặp lại ảnh nền liên tục
// -i: Đầu vào (ảnh và audio)
// -c:v libx264: Mã hóa video thành chuẩn H.264 rộng rãi
// -tune stillimage: Tối ưu hóa cho ảnh tĩnh để tiết kiệm băng thông máy chủ
// -c:a copy: Giữ nguyên codec âm thanh gốc không cần mã hóa lại để tránh mất chất lượng và giảm tải CPU
// -f mpegts: Xuất ra định dạng luồng phát IPTV tiêu chuẩn
// -: Đẩy dữ liệu trực tiếp ra luồng xuất của PHP
$ffmpeg_cmd = "ffmpeg -loop 1 -i " . escapeshellarg($image_url) . " -i " . escapeshellarg($audio_url) . " -c:v libx264 -tune stillimage -pix_fmt yuv420p -c:a copy -shortest -f mpegts -";

// 4. Mở luồng chạy câu lệnh và truyền dữ liệu real-time tới người xem
$fp = popen($ffmpeg_cmd, "r");
while (!feof($fp)) {
    echo fread($fp, 8192);
    flush(); // Đẩy dữ liệu đi ngay lập tức
}
pclose($fp);
?>