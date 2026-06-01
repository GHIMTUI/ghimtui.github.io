const http = require("http");
const fs = require("fs");

const targetUrl = "http://hoiquan.dpdns.org/VTVGo/?sctv4";

function requestWithBypass(url, retryCount = 0) {
    if (retryCount > 3) {
        console.log("Quá số lần chuyển hướng cho phép.");
        return;
    }

    console.log("Đang kết nối tới: " + url);
    
    http.get(url, {
        headers: { 
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
            "Cache-Control": "max-age=0",
            "Upgrade-Insecure-Requests": "1",
            "Connection": "keep-alive"
        }
    }, (res) => {
        // Trường hợp 1: Chuyển hướng 301, 302, 307
        if ([301, 302, 307].includes(res.statusCode) && res.headers.location) {
            let realUrl = res.headers.location.trim();
            
            if (realUrl.startsWith("/")) {
                realUrl = "http://hoiquan.dpdns.org" + realUrl;
            }

            if (realUrl.includes("m3u8") || realUrl.includes("vtvgo.vn") || retryCount === 2) {
                if (!realUrl.endsWith(".m3u8")) {
                    realUrl = realUrl.includes("?") ? realUrl + "&file=.m3u8" : realUrl + "?file=.m3u8";
                }
                fs.writeFileSync("link_sctv.txt", realUrl);
                console.log("=== BÓC TÁCH THÀNH CÔNG ===");
                console.log("Đã lưu vào link_sctv.txt: " + realUrl);
            } else {
                requestWithBypass(realUrl, retryCount + 1);
            }
        } 
        // Trường hợp 2: Trả về mã 200, tìm link ẩn trong HTML bằng Regex
        else if (res.statusCode === 200) {
            let data = "";
            res.on("data", (chunk) => { data += chunk; });
            res.on("end", () => {
                const m3u8Regex = /(https?:\/\/[^\s"']+\.m3u8[^\s"']*)/i;
                const match = data.match(m3u8Regex);
                
                if (match && match[1]) {
                    let realUrl = match[1].trim();
                    if (!realUrl.endsWith(".m3u8")) {
                        realUrl = realUrl.includes("?") ? realUrl + "&file=.m3u8" : realUrl + "?file=.m3u8";
                    }
                    fs.writeFileSync("link_sctv.txt", realUrl);
                    console.log("=== BÓC TÁCH THÀNH CÔNG TỪ HTML ===");
                    console.log("Đã tìm thấy link: " + realUrl);
                } else {
                    console.log("=== THẤT BẠI ===");
                    console.log("Server trả về mã 200 nhưng không có link m3u8 nào ẩn bên trong.");
                }
            });
        } else {
            console.log("=== BỊ CHẶN ===");
            console.log("Mã lỗi: " + res.statusCode);
        }
    }).on("error", (err) => {
        console.error("Lỗi mạng: " + err.message);
    });
}

requestWithBypass(targetUrl);
