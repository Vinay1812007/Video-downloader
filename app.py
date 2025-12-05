from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import google.generativeai as genai

app = Flask(__name__)
CORS(app)

# --- AI CONFIGURATION ---
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

if GEMINI_KEY:
    try:
        genai.configure(api_key=GEMINI_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        print(f"AI Error: {e}")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    if not GEMINI_KEY:
        return jsonify({"text": "Error: AI Support is not configured in Render Settings."})
    
    data = request.json
    user_msg = data.get('message')
    
    try:
        # Disable safety filters to prevent random blocks on innocent queries
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
        ]
        
        prompt = f"You are S.V. Support. Be short and helpful. User: {user_msg}"
        response = model.generate_content(prompt, safety_settings=safety_settings)
        return jsonify({"text": response.text})
    except Exception as e:
        return jsonify({"text": "I am updating my servers. Please ask again in 10 seconds."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
