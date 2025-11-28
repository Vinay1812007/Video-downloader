from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests
import random
import time

app = Flask(__name__)
CORS(app)

# THE SWARM: A list of the strongest current API mirrors
# The code will cycle through these to find a working one.
API_MIRRORS = [
    "https://cobalt.steamship.site/api/json",
    "https://cobalt.q13.fr/api/json",
    "https://cobalt-api.ayo.tf/api/json",
    "https://co.wuk.sh/api/json",
    "https://cobalt.rudart.cc/api/json"
]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    data = request.json
    url = data.get('url')
    mode = data.get('mode', 'video') # 'video' or 'audio'

    if not url:
        return jsonify({"error": "No URL provided"})

    # Headers to mimic a real browser visit to the official tool
    # This prevents 403 Forbidden errors
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Origin": "https://cobalt.tools",
        "Referer": "https://cobalt.tools/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    }

    payload = {
        "url": url,
        "vQuality": "720",
        "filenamePattern": "basic",
        "isAudioOnly": (mode == 'audio')
    }

    # Shuffle mirrors to balance load
    mirrors = API_MIRRORS.copy()
    random.shuffle(mirrors)

    last_error = ""

    # Try each mirror until one works
    for api in mirrors:
        try:
            print(f"Swarm connecting to: {api}")
            resp = requests.post(api, json=payload, headers=headers, timeout=12)
            
            if resp.status_code == 200:
                data = resp.json()
                
                # Check if we got a valid link
                if 'url' in data or 'picker' in data:
                    return jsonify({"success": True, "data": data})
                
                if 'text' in data:
                    last_error = data['text']
            
        except Exception as e:
            last_error = str(e)
            continue

    # If all fail
    return jsonify({"success": False, "error": "Server Busy. Please try again in 10 seconds."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
