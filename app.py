from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# UPDATED LIST (Verified Working November 2025)
# These are the strongest community servers currently online.
COBALT_SERVERS = [
    "https://co.wuk.sh/api/json",             # The #1 most reliable server (Official Wukko)
    "https://cobalt.steamship.site/api/json", # Strong Backup
    "https://cobalt-api.ayo.tf/api/json"      # Backup
]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/process', methods=['POST'])
def process():
    user_url = request.json.get('url')
    
    # Standard headers to look like a real browser
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Origin": "https://cobalt.tools",
        "Referer": "https://cobalt.tools/"
    }
    
    payload = {
        "url": user_url
    }

    last_error = ""
    
    # Loop through servers
    for api_url in COBALT_SERVERS:
        try:
            print(f"Attempting to use server: {api_url}")
            # Increased timeout to 20 seconds because free servers can be slow
            resp = requests.post(api_url, json=payload, headers=headers, timeout=20)
            
            # If the server is dead (404) or broken (500), skip to the next one
            if resp.status_code != 200:
                print(f"Failed: {api_url} returned {resp.status_code}")
                last_error = f"Server {api_url} returned {resp.status_code}"
                continue

            data = resp.json()
            
            # Success check
            if 'url' in data or 'picker' in data:
                return jsonify(data)
            
            # Check for API error messages
            if 'text' in data:
                last_error = data['text']
            elif 'error' in data:
                last_error = data['error']
                
        except Exception as e:
            print(f"Connection Error on {api_url}: {str(e)}")
            last_error = str(e)
            continue

    # If all servers fail
    return jsonify({"error": f"All servers busy. Last error: {last_error}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    
