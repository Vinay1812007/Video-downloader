from flask import Flask, render_template, request, jsonify
import requests
import random

app = Flask(__name__)

# THE "ELITE" LIST (Verified Working Servers)
# We prioritize the official and high-uptime community servers.
SERVERS = [
    "https://co.wuk.sh/api/json",              # Official Server (Best Quality)
    "https://cobalt.steamship.site/api/json",  # Very Stable
    "https://cobalt-api.ayo.tf/api/json",      # reliable backup
    "https://api.cobalt.tools/api/json"        # Official backup
]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    user_url = data.get('url')
    
    if not user_url:
        return jsonify({"status": "error", "text": "No URL provided"})

    # MAGIC HEADERS
    # These headers are REQUIRED to make the official server (co.wuk.sh) accept the request.
    # Without them, it blocks you as a "bot".
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Origin": "https://cobalt.tools",
        "Referer": "https://cobalt.tools/"
    }

    payload = {
        "url": user_url,
        "filenamePattern": "basic"
    }

    last_error = ""

    # Rotator Logic: Shuffle the list so we don't hammer one server
    # This prevents rate-limiting.
    active_servers = SERVERS.copy()
    random.shuffle(active_servers)

    for api_url in active_servers:
        try:
            print(f"Attempting: {api_url}")
            resp = requests.post(api_url, json=payload, headers=headers, timeout=12)
            
            if resp.status_code == 200:
                result = resp.json()
                
                # Check for success
                if 'url' in result or 'picker' in result:
                    return jsonify(result)
                
                # Check for specific API error text
                if 'text' in result:
                    last_error = f"{api_url} says: {result['text']}"
            else:
                last_error = f"{api_url} returned {resp.status_code}"
            
        except Exception as e:
            last_error = f"Connection failed to {api_url}"
            continue

    # If we get here, all servers failed
    return jsonify({"status": "error", "text": f"Service Busy. Please try again. ({last_error})"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
