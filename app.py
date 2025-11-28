from flask import Flask, render_template, request, jsonify
import requests
import random
import time

app = Flask(__name__)

# NEW "COMMUNITY" LIST (Less Strict)
# These servers are run by volunteers and usually don't block Render IPs.
SERVERS = [
    "https://cobalt.steamship.site/api/json",   # Very reliable
    "https://cobalt.q13.fr/api/json",           # French server (Fast)
    "https://cobalt.rudart.cc/api/json",        # Backup 1
    "https://cobalt.mashed.pw/api/json",        # Backup 2
    "https://cobalt-api.ayo.tf/api/json"        # Backup 3
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

    # SIMPLE HEADERS
    # We removed the 'Origin' and 'Referer' spoofing because it was causing the 403 Block.
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)" 
    }

    payload = {
        "url": user_url,
        "filenamePattern": "basic"
    }

    last_error = ""

    # Shuffle servers to distribute load
    active_servers = SERVERS.copy()
    random.shuffle(active_servers)

    for api_url in active_servers:
        try:
            print(f"Trying: {api_url}")
            # Increased timeout to 15s for slow community servers
            resp = requests.post(api_url, json=payload, headers=headers, timeout=15)
            
            if resp.status_code == 200:
                result = resp.json()
                
                # Success Check
                if 'url' in result or 'picker' in result:
                    return jsonify(result)
                
                if 'text' in result:
                    last_error = result['text']
            
            # If 403/429/500, just log it and move to next
            print(f"Failed {api_url}: {resp.status_code}")
            last_error = f"Server returned {resp.status_code}"
            
        except Exception as e:
            print(f"Error {api_url}: {str(e)}")
            last_error = str(e)
            continue

    return jsonify({"status": "error", "text": f"All servers busy. Last error: {last_error}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
