const fs = require('fs');

// Cấu hình danh sách các kênh cần getlink và cập nhật
const channels = [
    { id: 'sctvhdpth', url: 'http://hoiquan.dpdns.org/VTVGo/?sctvphim' },
    { id: 'sctv1hd',   url: 'http://hoiquan.dpdns.org/VTVGo/?sctv1' },
    { id: 'sctv4hd',   url: 'http://hoiquan.dpdns.org/VTVGo/?sctv4' },
    { id: 'sctv7hd',   url: 'http://hoiquan.dpdns.org/VTVGo/?sctv7' },
    { id: 'sctv8hd',   url: 'http://hoiquan.dpdns.org/VTVGo/?sctv8' },
    { id: 'sctv11hd',  url: 'http://hoiquan.dpdns.org/VTVGo/?sctv11' },
    { id: 'sctv13hd',  url: 'http://hoiquan.dpdns.org/VTVGo/?sctv13' },
    { id: 'sctv14hd',  url: 'http://hoiquan.dpdns.org/VTVGo/?sctv14' },
    { id: 'sctv18hd',  url: 'http://hoiquan.dpdns.org/VTVGo/?sctv18' },
    { id: 'sctv19hd',  url: 'http://hoiquan.dpdns.org/VTVGo/?sctv19' },
    { id: 'sctv21hd',  url: 'http://hoiquan.dpdns.org/VTVGo/?sctv21' }
];

const m3uFilePath = './tivi.m3u'; // Đường dẫn file m3u ở thư mục gốc

async function updateM3u() {
    try {
        if (!fs.existsSync(m3uFilePath)) {
            console.error(`Không tìm thấy file m3u tại đường dẫn: ${m3uFilePath}`);
            return;
        }

        // Đọc toàn bộ nội dung file m3u
        let m3uContent = fs.readFileSync(m3uFilePath, 'utf8');
        let isUpdated = false;

        for (const ch of channels) {
            try {
                // Gọi HEAD request lấy URL sau khi Redirect
                const response = await fetch(ch.url, { method: 'HEAD', redirect: 'follow' });
                const finalStreamUrl = response.url;

                if (!finalStreamUrl || finalStreamUrl === ch.url) {
                    console.error(`[${ch.id}] Không lấy được link redirect từ server, bỏ qua.`);
                    continue;
                }

                // REGEX CẢI TIẾN: Bỏ qua mọi loại khoảng trắng đặc biệt (\s), không phân biệt HOA/thường (i)
                const escapedId = ch.id.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
                const regex = new RegExp(`(#EXTINF:[^\\n\\r]*tvg-id\\s*=\\s*["']${escapedId}["'][^\\n\\r]*\\r?\\n)(http[^\\s\\r\\n]+)`, 'gi');

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

        // Ghi lại file nếu có thay đổi
        if (isUpdated) {
            fs.writeFileSync(m3uFilePath, m3uContent, 'utf8');
            console.log('--- Đã cập nhật xong toàn bộ danh sách kênh SCTV vào tivi.m3u ---');
        } else {
            console.log('Không có thay đổi nào được cập nhật (Có thể do trùng link cũ hoặc lệch cấu trúc hoàn toàn).');
        }

    } catch (error) {
        console.error('Lỗi hệ thống:', error);
    }
}

updateM3u();
