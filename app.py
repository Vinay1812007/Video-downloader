from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# NEW LIST (Updated Nov 2025) - Using reliable 'ggtyler' and 'ayo' mirrors
COBALT_SERVERS = [
    "https://nyc1.coapi.ggtyler.dev/api/json",   # US Server (Fastest)
    "https://par1.coapi.ggtyler.dev/api/json",   # Europe Server
    "https://cobalt-api.ayo.tf/api/json",        # Reliable Backup
    "https://dlapi.miichelle.moe/api/json"       # Backup 2
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
    
    payload = {
        "url": user_url
    }

    last_error = ""
    
    # Loop through the new server list
    for api_url in COBALT_SERVERS:
        try:
            print(f"Testing server: {api_url}")
            # Increased timeout to 15 seconds for slower connections
            resp = requests.post(api_url, json=payload, headers=headers, timeout=15)
            
            if resp.status_code != 200:
                last_error = f"Server {api_url} returned {resp.status_code}"
                continue

            data = resp.json()
            
            # Check if we got a valid link
            if 'url' in data or 'picker' in data:
                return jsonify(data)
            
            # Save error message if the server complained
            if 'text' in data:
                last_error = data['text']
            elif 'error' in data:
                 last_error = data['error']
                
        except Exception as e:
            last_error = str(e)
            continue

    # If all 4 servers fail
    return jsonify({"error": f"All mirrors failed. Last error: {last_error}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    
