const fs = require('fs');

async function updateM3u() {
    const getlinkUrl = 'http://hoiquan.dpdns.org/VTVGo/?sctv1';
    const m3uFilePath = './tivi.m3u'; // Đường dẫn tới file m3u của bạn

    try {
        // 1. Gọi fetch để lấy URL sau khi tự động Redirect
        const response = await fetch(getlinkUrl, { method: 'HEAD', redirect: 'follow' });
        const finalStreamUrl = response.url;

        console.log('Link stream mới lấy được:', finalStreamUrl);

        if (!finalStreamUrl || finalStreamUrl.includes('?sctv1')) {
            console.error('Không lấy được link redirect thực tế!');
            return;
        }

        // 2. Đọc nội dung file m3u hiện tại
        let m3uContent = fs.readFileSync(m3uFilePath, 'utf8');

        // 3. Dùng Regex để tìm và thay thế link bên dưới dòng SCTV1
        // Regex này tìm dòng #EXTINF có chứa tvg-id="sctv1hd" và thay thế link ngay phía sau nó
        const regex = /(#EXTINF:.*tvg-id="sctv1hd"[\s\S]*?\n)(http[^\s]+)/g;
        
        if (regex.test(m3uContent)) {
            m3uContent = m3uContent.replace(regex, `$1${finalStreamUrl}`);
            fs.writeFileSync(m3uFilePath, m3uContent, 'utf8');
            console.log('Đã cập nhật link SCTV1 mới vào file m3u thành công!');
        } else {
            console.error('Không tìm thấy dòng cấu hình SCTV1 trong file m3u!');
        }

    } catch (error) {
        console.error('Lỗi trong quá trình xử lý:', error);
    }
}

updateM3u();