const express = require('express');
const ffmpeg = require('fluent-ffmpeg');
const app = express();
const PORT = process.env.PORT || 3000;

app.get('/radio.ts', (req, res) => {
    // 1. Cấu hình header để app IPTV nhận diện đây là luồng Video MPEG-TS
    res.setHeader('Content-Type', 'video/mp4');
    res.setHeader('Cache-Control', 'no-cache, must-revalidate');

    const imageUrl = "https://media.baotayninh.vn/upload/channel/2d07bdc676fe7d422bda35e1f5170c47.jpg";
    const audioUrl = "http://live-hq.evgcdn.net/live/2851dd3d9016ac74d84b0c4a7a659f76891/chunklist.m3u8";

    // 2. Chạy FFmpeg trộn ảnh tĩnh và âm thanh radio
    ffmpeg()
        .input(imageUrl)
        .inputOptions(['-loop 1']) // Lặp lại ảnh nền liên tục
        .input(audioUrl)
        .outputOptions([
            '-c:v libx264',          // Mã hóa video chuẩn H.264
            '-tune stillimage',      // Tối ưu riêng cho ảnh tĩnh để mượt và nhẹ
            '-pix_fmt yuv420p',      // Định dạng pixel chuẩn cho đầu phát IPTV
            '-c:a copy',             // Giữ nguyên âm thanh gốc, không tốn CPU transcode
            '-f mpegts'              // Định dạng luồng phát IPTV tiêu chuẩn
        ])
        .on('error', (err) => {
            console.log('Lỗi phát luồng: ' + err.message);
        })
        .pipe(res, { end: true }); // Truyền trực tiếp dữ liệu video ra cho người xem
});

app.listen(PORT, () => {
    console.log(`Server chạy tại port ${PORT}`);
});