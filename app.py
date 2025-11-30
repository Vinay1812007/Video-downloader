from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests
import random
import os
import google.generativeai as genai

app = Flask(__name__)
CORS(app)

# --- CONFIGURATION ---
SERVERS = [
    "https://cobalt.steamship.site/api/json",
    "https://cobalt.rudart.cc/api/json", 
    "https://cobalt.q13.fr/api/json",
    "https://cobalt-api.ayo.tf/api/json",
    "https://api.cobalt.tools/api/json"
]

# Configure AI
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

if GEMINI_KEY:
    try:
        genai.configure(api_key=GEMINI_KEY)
        # We use the standard model without system_instruction in constructor for maximum compatibility
        model = genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        print(f"AI Config Error: {e}")

@app.route('/')
def home():
    return render_template('index.html')

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

@app.route('/chat', methods=['POST'])
def chat():
    if not GEMINI_KEY:
        return jsonify({"text": "Error: API Key is missing in Render Settings."})
    
    data = request.json
    user_msg = data.get('message')
    
    try:
        # 1. Add System Instruction manually to the prompt (Safer)
        full_prompt = f"System: You are a helpful support assistant for S.V. Downloader. Keep answers short.\nUser: {user_msg}"
        
        # 2. Disable Safety Filters (Prevents random blocks)
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
        ]

        response = model.generate_content(full_prompt, safety_settings=safety_settings)
        return jsonify({"text": response.text})
        
    except Exception as e:
        # DEBUG MODE: This will show the REAL error on your screen
        return jsonify({"text": f"System Error: {str(e)}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    
