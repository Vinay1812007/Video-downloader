from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests
import random

app = Flask(__name__)
CORS(app)

# THE "LENIENT" LIST
# These servers are known to accept traffic from Cloud IPs (like Render).
# We removed the official servers because they are too strict.
SERVERS = [
    "https://cobalt.steamship.site/api/json",   # Very Lenient
    "https://cobalt.rudart.cc/api/json",        # Lenient
    "https://cobalt.q13.fr/api/json",           # Good European server
    "https://cobalt-api.ayo.tf/api/json",       # Backup
    "https://api.cobalt.tools/api/json"         # Fallback
]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    data = request.json
    url = data.get('url')

    if not url:
        return jsonify({"success": False, "error": "No URL provided"})

    # CLEAN HEADERS
    # We removed 'Origin' and 'Referer'. 
    # Sending 'Origin: cobalt.tools' from Render was causing the 403 Forbidden error.
    # We now look like a generic script, which these community servers allow.
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    }

    payload = {
        "url": url,
        "filenamePattern": "basic"
    }

    # Shuffle to balance load
    active_servers = SERVERS.copy()
    random.shuffle(active_servers)

    last_error = ""

    for api_url in active_servers:
        try:
            print(f"Connecting to: {api_url}")
            # Timeout set to 15s for stability
            resp = requests.post(api_url, json=payload, headers=headers, timeout=15)
            
            if resp.status_code == 200:
                data = resp.json()
                
                # Check if we got a link
                if 'url' in data or 'picker' in data:
                    return jsonify({"success": True, "data": data})
                
                if 'text' in data:
                    last_error = data['text']
            else:
                last_error = f"Status {resp.status_code}"
                
        except Exception as e:
            last_error = str(e)
            continue

    return jsonify({"success": False, "error": f"Servers are busy. Last error: {last_error}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
