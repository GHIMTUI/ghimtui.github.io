const axios = require('axios');
const fs = require('fs');

const targetUrl = "http://hoiquan.dpdns.org/VTVGo/?sctv4";

async function extractLink() {
    try {
        console.log("Đang tiến hành bóc tách vỏ qua Axios...");
        
        // Gửi request với đầy đủ cấu hình giả lập trình duyệt di động sâu
        const response = await axios.get(targetUrl, {
            headers: {
                'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
                'Referer': 'http://hoiquan.dpdns.org/',
                'Origin': 'http://hoiquan.dpdns.org',
                'Connection': 'keep-alive',
                'Cache-Control': 'max-age=0'
            },
            maxRedirects: 5, // Tự động đi xuyên qua tối đa 5 lớp vỏ redirect
            validateStatus: function (status) {
                return status >= 200 && status < 400; // Nhận hết các mã phản hồi từ 200 đến 399
            }
        });

        // Lấy URL cuối cùng sau khi đã đi xuyên qua các lớp chuyển hướng
        let realUrl = response.request.res.responseUrl || targetUrl;
        
        // Nếu trường hợp server trả về mã 200 và giấu link trong nội dung HTML
        if (realUrl === targetUrl || !realUrl.includes('m3u8')) {
            const htmlContent = response.data;
            const m3u8Regex = /(https?:\/\/[^\s"']+\.m3u8[^\s"']*)/i;
            const match = htmlContent.match(m3u8Regex);
            if (match && match[1]) {
                realUrl = match[1].trim();
            }
        }

        // Kiểm tra và ép định dạng đuôi .m3u8 cho chuẩn chỉnh
        if (realUrl && (realUrl.includes('m3u8') || realUrl.includes('vtvgo'))) {
            if (!realUrl.endsWith(".m3u8")) {
                realUrl = realUrl.includes("?") ? realUrl + "&file=.m3u8" : realUrl + "?file=.m3u8";
            }
            
            // Ghi kết quả vào file txt
            fs.writeFileSync("link_sctv.txt", realUrl);
            console.log("=== BÓC TÁCH THÀNH CÔNG ===");
            console.log("Link thu được: " + realUrl);
        } else {
            console.log("=== THẤT BẠI ===");
            console.log("Không tìm thấy đường link m3u8 nào hợp lệ.");
        }

    } catch (error) {
        console.error("Lỗi trong quá trình bóc vỏ: " + error.message);
        if (error.response) {
            console.log("Mã phản hồi từ Server: " + error.response.status);
        }
    }
}

extractLink();
