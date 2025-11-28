from flask import Flask, render_template, request, jsonify
import requests
import random

app = Flask(__name__)

# SWARM: List of Cobalt APIs (The Engines)
# We try them one by one until one works.
SERVERS = [
    "https://cobalt.steamship.site/api/json",  # Usually most reliable
    "https://co.wuk.sh/api/json",              # Official (Strict)
    "https://cobalt-api.ayo.tf/api/json",       # Good backup
    "https://cobalt.kwiatekmiki.pl/api/json"   # Backup
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

    # Headers to make the request look like a real user
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

    # Loop through the servers (The Swarm Logic)
    for api_url in SERVERS:
        try:
            print(f"Trying server: {api_url}")
            resp = requests.post(api_url, json=payload, headers=headers, timeout=10)
            
            if resp.status_code == 200:
                result = resp.json()
                # Check if we actually got a valid response
                if 'url' in result or 'picker' in result:
                    return jsonify(result)
            
            # Save error for debugging
            last_error = f"{api_url} -> {resp.status_code}"
            
        except Exception as e:
            last_error = str(e)
            continue

    # If all fail
    return jsonify({"status": "error", "text": f"All servers busy. Last error: {last_error}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
