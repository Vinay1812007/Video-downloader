from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/process', methods=['POST'])
def process():
    try:
        user_url = request.json.get('url')
        
        # This is the "Middleman" logic
        # The server sends the link to the API, so your browser doesn't have to.
        api_url = "https://api.cobalt.tools/api/json"
        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        payload = {
            "url": user_url,
            "vQuality": "720"
        }
        
        # Server talks to External API
        resp = requests.post(api_url, json=payload, headers=headers)
        return jsonify(resp.json())

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
        
