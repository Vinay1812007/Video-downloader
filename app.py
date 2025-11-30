from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests
import random
import os
import google.generativeai as genai

app = Flask(__name__)
CORS(app)

# --- CONFIGURATION ---
# 1. DOWNLOADER SERVERS (The Swarm)
SERVERS = [
    "https://cobalt.steamship.site/api/json",
    "https://cobalt.rudart.cc/api/json", 
    "https://cobalt.q13.fr/api/json",
    "https://cobalt-api.ayo.tf/api/json",
    "https://api.cobalt.tools/api/json"
]

# 2. GEMINI AI CONFIGURATION
# It tries to find the API key in Render's settings.
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)
    # Use the lightweight "Flash" model for speed
    model = genai.GenerativeModel('gemini-1.5-flash', system_instruction="You are a helpful support assistant for 'S.V. Downloader'. You help users download videos from YouTube, Instagram, and TikTok. Keep answers short and friendly.")

@app.route('/')
def home():
    return render_template('index.html')

# --- DOWNLOADER ROUTE ---
@app.route('/process', methods=['POST'])
def process():
    data = request.json
    url = data.get('url')

    if not url:
        return jsonify({"success": False, "error": "No URL provided"})

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    }

    payload = { "url": url, "filenamePattern": "basic" }

    active_servers = SERVERS.copy()
    random.shuffle(active_servers)
    last_error = ""

    for api_url in active_servers:
        try:
            resp = requests.post(api_url, json=payload, headers=headers, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                if 'url' in data or 'picker' in data:
                    return jsonify({"success": True, "data": data})
                if 'text' in data:
                    last_error = data['text']
        except Exception as e:
            last_error = str(e)
            continue

    return jsonify({"success": False, "error": f"Busy. Last error: {last_error}"})

# --- NEW: SUPPORT CHAT ROUTE ---
@app.route('/chat', methods=['POST'])
def chat():
    if not GEMINI_KEY:
        return jsonify({"text": "Error: AI Support is not configured yet (Missing API Key)."})
    
    data = request.json
    user_msg = data.get('message')
    
    try:
        # Ask Gemini
        response = model.generate_content(user_msg)
        return jsonify({"text": response.text})
    except Exception as e:
        return jsonify({"text": "Sorry, I am having trouble connecting right now."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    
