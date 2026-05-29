const fs = require('fs');

// Danh sách cấu hình chuẩn tương ứng với ID trong file m3u của bạn
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

const m3uFilePath = '../file/viti.m3u';

async function updateM3u() {
    try {
        if (!fs.existsSync(m3uFilePath)) {
            console.error(`Không tìm thấy file m3u tại đường dẫn: ${m3uFilePath}`);
            return;
        }

        let m3uContent = fs.readFileSync(m3uFilePath, 'utf8');
        let isUpdated = false;

        for (const ch of channels) {
            try {
                // Thực hiện gọi lấy link stream mới nhất từ server getlink
                const response = await fetch(ch.url, { method: 'HEAD', redirect: 'follow' });
                const finalStreamUrl = response.url;

                if (!finalStreamUrl || finalStreamUrl === ch.url) {
                    console.error(`[${ch.id}] Không lấy được link redirect từ server.`);
                    continue;
                }

                // REGEX NÂNG CAO: Chấp tất cả các loại khoảng trắng ẩn, khoảng trắng dư thừa cuối dòng và dấu xuống dòng \r\n
                const escapedId = ch.id.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
                const regex = new RegExp(`(#EXTINF:[^\\n\\r]*tvg-id\\s*=\\s*["']${escapedId}["'][^\\n\\r]*(?:\\r?\\n)+)(http[^\\s\\r\\n]+)`, 'gi');

                if (regex.test(m3uContent)) {
                    m3uContent = m3uContent.replace(regex, `$1${finalStreamUrl}`);
                    console.log(`[${ch.id}] -> Đã tìm thấy vị trí và thay thế link mới thành công.`);
                    isUpdated = true;
                } else {
                    console.warn(`[${ch.id}] Không tìm thấy dòng chứa tvg-id="${ch.id}" trong file m3u.`);
                }
            } catch (err) {
                console.error(`Lỗi xử lý kênh ${ch.id}:`, err.message);
            }
        }

        // Lưu lại file tivi.m3u nếu có sự thay đổi link
        if (isUpdated) {
            fs.writeFileSync(m3uFilePath, m3uContent, 'utf8');
            console.log('--- ĐÃ GHI ĐÈ VÀ CẬP NHẬT THÀNH CÔNG FILE TIVI.M3U ---');
        } else {
            console.log('Không có thay đổi nào được cập nhật vào file.');
        }

    } catch (error) {
        console.error('Lỗi hệ thống tổng quan:', error);
    }
}

updateM3u();
