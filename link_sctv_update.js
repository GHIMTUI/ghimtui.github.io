const fs = require('fs');
const path = require('path');

const CHANNELS_API = {
    "SCTV Phim Tổng Hợp": "https://hoiquan.dpdns.org/VTVGo/?sctvphim",
    "SCTV1": "https://hoiquan.dpdns.org/VTVGo/?sctv1",
    "SCTV4": "https://hoiquan.dpdns.org/VTVGo/?sctv4",
    "SCTV8": "https://hoiquan.dpdns.org/VTVGo/?sctv8",
    "SCTV11": "https://hoiquan.dpdns.org/VTVGo/?sctv11",
    "SCTV13": "https://hoiquan.dpdns.org/VTVGo/?sctv13",
    "SCTV14": "https://hoiquan.dpdns.org/VTVGo/?sctv14",
    "SCTV18": "https://hoiquan.dpdns.org/VTVGo/?sctv18",
    "SCTV19": "https://hoiquan.dpdns.org/VTVGo/?sctv19",
    "SCTV21": "https://hoiquan.dpdns.org/VTVGo/?sctv21"
};

const TXT_FILE_PATH = path.join(__dirname, 'file', 'link_sctv_update.txt');
const M3U_FILE_PATH = path.join(__dirname, 'tivi.m3u');

async function getNewM3u8(api_url) {
    try {
        const response = await fetch(api_url, {
            method: 'GET',
            headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
                'Referer': 'https://hoiquan.dpdns.org/',
                // Đánh lừa máy chủ rằng request này đến từ một client Việt Nam
                'X-Forwarded-For': '113.161.11.11', 
                'Client-IP': '113.161.11.11'
            },
            redirect: 'follow' // Tự động đuổi theo link chuyển hướng m3u8
        });

        if (response.ok) {
            // Nếu web trả về link trực tiếp dạng text
            const content = (await response.text()).trim();
            if (content.startsWith('http')) {
                return content;
            }
            // Nếu web redirect thẳng tới link m3u8 đích
            if (response.url && response.url !== api_url) {
                return response.url;
            }
        }
    } catch (error) {
        // Không in ra lỗi chi tiết để tránh rối màn hình
    }
    return null;
}

async function main() {
    console.log("--- BƯỚC 1: Lấy link bằng Node.js và lưu ra file txt ---");
    
    // Tự động tạo thư mục 'file' nếu chưa có
    const dir = path.dirname(TXT_FILE_PATH);
    if (!fs.existsSync(dir)){
        fs.mkdirSync(dir, { recursive: true });
    }

    const fetchedLinks = {};
    let txtContent = "";

    for (const [channel, api] of Object.entries(CHANNELS_API)) {
        const newLink = await getNewM3u8(api);
        if (newLink) {
            txtContent += `${channel}|${newLink}\n`;
            fetchedLinks[channel] = newLink;
            console.log(`[+] Thành công: ${channel}`);
        } else {
            console.log(`[-] Thất bại: ${channel}`);
        }
    }

    if (Object.keys(fetchedLinks).length === 0) {
        console.log("Không có link nào được tải về, bỏ qua cập nhật tivi.m3u.");
        return;
    }

    // Ghi file txt trung gian
    fs.writeFileSync(TXT_FILE_PATH, txtContent, 'utf-8');

    console.log("\n--- BƯỚC 2: Cập nhật ngược vào tivi.m3u ---");
    if (!fs.existsSync(M3U_FILE_PATH)) {
        console.log(`Không tìm thấy file ${M3U_FILE_PATH}`);
        return;
    }

    let m3uContent = fs.readFileSync(M3U_FILE_PATH, 'utf-8');
    let lines = m3uContent.split(/\r?\n/);
    let updated = false;

    for (let i = 0; i < lines.length; i++) {
        if (lines[i].startsWith("#EXTINF")) {
            for (const [channelName, newLink] of Object.entries(fetchedLinks)) {
                if (lines[i].includes(`,${channelName}`)) {
                    if (i + 1 < lines.length && lines[i+1].startsWith("http")) {
                        if (lines[i+1].trim() !== newLink) {
                            lines[i+1] = newLink;
                            console.log(`Đã thay link mới cho: ${channelName}`);
                            updated = true;
                        } else {
                            console.log(`Link không đổi, giữ nguyên: ${channelName}`);
                        }
                    }
                    break;
                }
            }
        }
    }

    if (updated) {
        fs.writeFileSync(M3U_FILE_PATH, lines.join('\n'), 'utf-8');
        console.log(`\n=> Đã cập nhật file tivi.m3u thành công!`);
    } else {
        console.log("\n=> Không có thay đổi nào được ghi.");
    }
}

main();
