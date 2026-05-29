const fs = require('fs');

// Cấu hình danh sách các kênh cần getlink và cập nhật
const channels = [
    { id: 'sctvhdpth', url: 'https://hoiquan.dpdns.org/VTVGo/?sctvphim' },
    { id: 'sctv1hd',   url: 'https://hoiquan.dpdns.org/VTVGo/?sctv1' },
    { id: 'sctv4hd',   url: 'https://hoiquan.dpdns.org/VTVGo/?sctv4' },
    { id: 'sctv7hd',   url: 'https://hoiquan.dpdns.org/VTVGo/?sctv7' },
    { id: 'sctv8hd',   url: 'https://hoiquan.dpdns.org/VTVGo/?sctv8' },
    { id: 'sctv11hd',  url: 'https://hoiquan.dpdns.org/VTVGo/?sctv11' },
    { id: 'sctv13hd',  url: 'https://hoiquan.dpdns.org/VTVGo/?sctv13' },
    { id: 'sctv14hd',  url: 'https://hoiquan.dpdns.org/VTVGo/?sctv14' },
    { id: 'sctv18hd',  url: 'https://hoiquan.dpdns.org/VTVGo/?sctv18' },
    { id: 'sctv19hd',  url: 'https://hoiquan.dpdns.org/VTVGo/?sctv19' },
    { id: 'sctv21hd',  url: 'https://hoiquan.dpdns.org/VTVGo/?sctv21' }
];

const m3uFilePath = './tivi.m3u'; // Đường dẫn file m3u của bạn

async function updateM3u() {
    try {
        if (!fs.existsSync(m3uFilePath)) {
            console.error(`Không tìm thấy file m3u tại đường dẫn: ${m3uFilePath}`);
            return;
        }

        // Đọc toàn bộ nội dung file m3u một lần duy nhất
        let m3uContent = fs.readFileSync(m3uFilePath, 'utf8');
        let isUpdated = false;

        for (const ch of channels) {
            try {
                // Gọi HEAD request lấy URL sau khi Redirect
                const response = await fetch(ch.url, { method: 'HEAD', redirect: 'follow' });
                const finalStreamUrl = response.url;

                if (!finalStreamUrl || finalStreamUrl === ch.url) {
                    console.error(`[${ch.id}] Không lấy được link redirect, bỏ qua.`);
                    continue;
                }

                // Tạo Regex tìm đúng dòng tvg-id của từng kênh và bắt link dòng kế tiếp
                const escapedId = ch.id.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
                const regex = new RegExp(`(#EXTINF:[^\\n]*tvg-id="${escapedId}"[^\\n]*\\r?\\n)(http[^\\s\\r\\n]+)`, 'gi');
                
                if (regex.test(m3uContent)) {
                    m3uContent = m3uContent.replace(regex, `$1${finalStreamUrl}`);
                    console.log(`[${ch.id}] -> Lấy link mới thành công.`);
                    isUpdated = true;
                } else {
                    console.warn(`[${ch.id}] Không tìm thấy tvg-id="${ch.id}" trong file m3u.`);
                }
            } catch (err) {
                console.error(`Lỗi xử lý kênh ${ch.id}:`, err.message);
            }
        }

        // Chỉ ghi lại file nếu có ít nhất 1 kênh thay đổi link thành công
        if (isUpdated) {
            fs.writeFileSync(m3uFilePath, m3uContent, 'utf8');
            console.log('--- Đã cập nhật xong toàn bộ danh sách kênh SCTV vào tivi.m3u ---');
        } else {
            console.log('Không có thay đổi nào được cập nhật.');
        }

    } catch (error) {
        console.error('Lỗi tổng quan hệ thống:', error);
    }
}

updateM3u();
