const { chromium } = require('playwright');
const fs = require('fs');

(async () => {
  // Khởi chạy trình duyệt với cấu hình giả lập sâu hơn
  const browser = await chromium.launch({ 
    headless: true,
    args: [
      '--disable-blink-features=AutomationControlled', // Ẩn biến tự động hóa của robot
      '--no-sandbox',
      '--disable-setuid-sandbox'
    ]
  });
  
  // Tạo context với User-Agent thật và kích thước màn hình phổ biến
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    viewport: { width: 1280, height: 720 },
    extraHTTPHeaders: {
      'Referer': 'https://hoiquan.dpdns.org/VTVGo/'
    }
  });

  const page = await context.newPage();
  let m3u8Url = '';

  // Lắng nghe tất cả các request để bắt link m3u8
  page.on('request', request => {
    const url = request.url();
    // Bắt các link m3u8 từ vtvgo hoặc hệ thống CDN
    if (url.includes('.m3u8')) {
      console.log('-> Phát hiện URL mạng:', url);
      m3u8Url = url;
    }
  });

  try {
    console.log('Đang truy cập trang web...');
    await page.goto('https://hoiquan.dpdns.org/VTVGo/?sctv7', {
      waitUntil: 'domcontentloaded', // Đợi cấu trúc trang load xong trước
      timeout: 60000
    });
    
    // Cuộn trang xuống một chút để giả lập hành vi người dùng
    await page.evaluate(() => window.scrollBy(0, 300));
    
    console.log('Đợi luồng dữ liệu video tải (15 giây)...');
    await page.waitForTimeout(15000); 

    // CHỤP ẢNH MÀN HÌNH ĐỂ KIỂM TRA (Sẽ lưu thành file trong repo để bạn xem có bị Cloudflare chặn không)
    await page.screenshot({ path: 'screenshot.png' });
    console.log('Đã chụp ảnh màn hình debug tại screenshot.png');

  } catch (error) {
    console.error('Lỗi trong quá trình chạy:', error);
  }

  // Ghi kết quả
  if (m3u8Url) {
    console.log('THÀNH CÔNG! Đã tìm thấy link m3u8:', m3u8Url);
    fs.writeFileSync('sctv_link.txt', m3u8Url, 'utf8');
  } else {
    console.log('THẤT BẠI: Không tìm thấy link m3u8 nào sau 15 giây chờ.');
    fs.writeFileSync('sctv_link.txt', 'Không tìm thấy link - Có thể bị chặn IP', 'utf8');
  }

  await browser.close();
})();
