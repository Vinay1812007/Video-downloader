from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# List of backup servers (Mirrors)
COBALT_SERVERS = [
    "https://cobalt.kwiatekmiki.pl/api/json",
    "https://cobalt.xy2401.top/api/json",
    "https://api.cobalt.tools/api/json" 
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
        "url": user_url,
        "vQuality": "720"
    }

    # Loop through servers until one works
    last_error = ""
    for api_url in COBALT_SERVERS:
        try:
            print(f"Trying server: {api_url}")
            resp = requests.post(api_url, json=payload, headers=headers, timeout=10)
            data = resp.json()
            
            # If we got a valid download link, stop and send it to user
            if 'url' in data or 'picker' in data:
                return jsonify(data)
            
            # If server returned an error text, save it
            if 'text' in data:
                last_error = data['text']
                
        except Exception as e:
            last_error = str(e)
            continue # Try next server

    # If all servers failed
    return jsonify({"error": f"Failed on all servers. Last error: {last_error}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    
