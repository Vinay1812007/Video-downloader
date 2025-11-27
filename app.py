from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# UPDATED LIST: 5 Fresh Working Servers (November 2025)
# We removed the dead 'api.cobalt.tools'
COBALT_SERVERS = [
    "https://co.wuk.sh/api/json",           # The most reliable backup
    "https://cobalt.steamship.site/api/json",
    "https://cobalt.rayrad.net/api/json",
    "https://cobalt.kwiatekmiki.pl/api/json",
    "https://cobalt.xy2401.top/api/json"
]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/process', methods=['POST'])
def process():
    user_url = request.json.get('url')
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    # Simplified payload (Removed 'vQuality' to prevent errors on some servers)
    payload = {
        "url": user_url
    }

    last_error = ""
    success = False
    
    for api_url in COBALT_SERVERS:
        try:
            print(f"Testing server: {api_url}")
            resp = requests.post(api_url, json=payload, headers=headers, timeout=12)
            
            # Check if server is actually happy (Status 200)
            if resp.status_code != 200:
                last_error = f"Server {api_url} returned {resp.status_code}"
                continue

            data = resp.json()
            
            # SUCCESS CHECK: Does it have a download link?
            if 'url' in data or 'picker' in data:
                return jsonify(data)
            
            # If server returned a specific error text (like "sign in required")
            if 'text' in data:
                last_error = data['text']
            elif 'error' in data:
                 last_error = data['error']
                
        except Exception as e:
            last_error = str(e)
            continue # Try next server in the list

    # If we get here, ALL servers failed
    return jsonify({"error": f"All servers busy. Last error: {last_error}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    
