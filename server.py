#!/usr/bin/env python3
"""
Simple static file server – serves index.html and send.js from the current folder.
Optionally exposes a public ngrok link for sharing.
"""

import os
import time
import threading
from flask import Flask, send_from_directory

PORT = 5000
USE_NGROK = True          # Set False to run locally only
NGROK_AUTH_TOKEN = None   # Optional: put your ngrok token here

app = Flask(__name__)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

# ------------------------------------------------------------
# Ngrok tunnel (runs in background)
# ------------------------------------------------------------
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

# ------------------------------------------------------------
if __name__ == '__main__':
    # Check that your files exist (just a warning)
    if not os.path.exists('index.html'):
        print("⚠️  Warning: index.html not found in current folder.")
    if not os.path.exists('send.js'):
        print("⚠️  Warning: send.js not found in current folder.")

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
