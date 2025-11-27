from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# THE BIG 3: The most reliable servers as of Late 2025
COBALT_SERVERS = [
    "https://cobalt.steamship.site/api/json",  # Often reliable
    "https://co.wuk.sh/api/json",              # Official (Strict)
    "https://cobalt-api.ayo.tf/api/json"       # Backup
]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/process', methods=['POST'])
def process():
    user_url = request.json.get('url')
    
    # MAGIC HEADERS: These trick the server into thinking we are the official site
    # This bypasses many "Bot" blocks
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Origin": "https://cobalt.tools",
        "Referer": "https://cobalt.tools/"
    }
    
    payload = {
        "url": user_url,
        "filenamePattern": "basic" # Keeps filenames simple
    }

    last_error = ""
    
    # Try each server one by one
    for api_url in COBALT_SERVERS:
        try:
            print(f"Trying server: {api_url}")
            # Timeout set to 15s to give free servers time to wake up
            resp = requests.post(api_url, json=payload, headers=headers, timeout=15)
            
            # 200 means Success
            if resp.status_code == 200:
                data = resp.json()
                # Double check we actually got a link
                if 'url' in data or 'picker' in data:
                    return jsonify(data)
            
            # If we failed, save the error message
            try:
                err_text = resp.json().get('text') or resp.json().get('error') or resp.text
                last_error = f"{api_url} said: {err_text}"
            except:
                last_error = f"{api_url} returned status {resp.status_code}"
                
            print(f"Failed: {last_error}")

        except Exception as e:
            last_error = f"Connection error to {api_url}: {str(e)}"
            continue

    # If everything failed, send the error to your phone
    return jsonify({"error": f"All servers failed. Last specific error: {last_error}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    
