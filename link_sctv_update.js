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
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
            },
            redirect: 'follow'
        });

        if (response.ok) {
            const content = (await response.text()).trim();
            if (content.startsWith('http')) return content;
            if (response.url && response.url !== api_url) return response.url;
        }
    } catch (error) {
        console.log(`Lỗi kết nối kênh: ${api_url}`);
    }
    return null;
}

async function main() {
    console.log("=== BƯỚC 1: Lấy link sống từ mạng Việt Nam ===");
    const dir = path.dirname(TXT_FILE_PATH);
    if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });

    const fetchedLinks = {};
    let txtContent = "";

    for (const [channel, api] of Object.entries(CHANNELS_API)) {
        const newLink = await getNewM3u8(api);
        if (newLink) {
            txtContent += `${channel}|${newLink}\n`;
            fetchedLinks[channel] = newLink;
            console.log(`[+] Lấy thành công: ${channel}`);
        } else {
            console.log(`[-] Thất bại: ${channel}`);
        }
    }

    if (Object.keys(fetchedLinks).length === 0) return;
    fs.writeFileSync(TXT_FILE_PATH, txtContent, 'utf-8');

    console.log("\n=== BƯỚC 2: Cập nhật vào tivi.m3u ===");
    if (!fs.existsSync(M3U_FILE_PATH)) {
        console.log("Không tìm thấy file tivi.m3u gốc tại thư mục này!");
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
                            console.log(`-> Thay link mới: ${channelName}`);
                            updated = true;
                        }
                    }
                    break;
                }
            }
        }
    }

    if (updated) {
        fs.writeFileSync(M3U_FILE_PATH, lines.join('\n'), 'utf-8');
        console.log("\n=> Đã cập nhật xong file tivi.m3u!");
    } else {
        console.log("\n=> Link vẫn trùng khớp, không cần ghi đè.");
    }
}

main();
