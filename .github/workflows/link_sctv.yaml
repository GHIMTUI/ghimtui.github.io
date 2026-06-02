const { chromium } = require('playwright');
const fs = require('fs');

(async () => {
  // Khởi chạy trình duyệt ẩn (headless)
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  
  let m3u8Url = '';

  // Bắt các request mạng để tìm link chứa .m3u8
  page.on('request', request => {
    const url = request.url();
    // Lọc tìm link m3u8 gốc (bỏ qua các link tracking hoặc phụ nếu có)
    if (url.includes('.m3u8') && !url.includes('analytics')) {
      m3u8Url = url;
    }
  });

  try {
    // Truy cập vào link của bạn
    await page.goto('https://hoiquan.dpdns.org/VTVGo/?sctv7', {
      waitUntil: 'networkidle', // Đợi cho đến khi mạng hết tải (đã load xong link video)
      timeout: 45000
    });
    
    // Đợi thêm 3 giây cho chắc chắn script player đã chạy
    await page.waitForTimeout(3000); 
  } catch (error) {
    console.error('Lỗi khi tải trang:', error);
  }

  // Kiểm tra nếu tìm thấy link thì ghi vào file
  if (m3u8Url) {
    console.log('Đã tìm thấy link M3U8:', m3u8Url);
    fs.writeFileSync('sctv_link.txt', m3u8Url, 'utf8');
    console.log('Đã lưu vào file sctv_link.txt thành công!');
  } else {
    console.log('Không tìm thấy link M3U8 nào.');
    // Ghi file rỗng hoặc báo lỗi để không bị giữ link cũ
    fs.writeFileSync('sctv_link.txt', 'Không tìm thấy link', 'utf8');
  }

  await browser.close();
})();
