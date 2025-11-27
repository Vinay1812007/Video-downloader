from flask import Flask, render_template, request, send_file, after_this_request, redirect
import yt_dlp
import os
import glob
import time
from fake_useragent import UserAgent

app = Flask(__name__)

DOWNLOAD_FOLDER = 'downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_video():
    video_url = request.form['url']
    
    # 1. YOUTUBE SAFE MODE
    # If a user accidentally hits "Enter" instead of the button, we handle it safely.
    if "youtube.com" in video_url or "youtu.be" in video_url:
        # Redirect to a working Cobalt instance that handles YouTube perfectly
        return redirect(f"https://cobalt.kwiatekmiki.pl/?url={video_url}")

    # 2. INSTAGRAM/TIKTOK ENGINE (The Python Logic that worked before)
    ua = UserAgent()
    random_ua = ua.random
    print(f"Processing Insta/Other: {video_url}")

    try:
        cleanup_downloads()
        
        ydl_opts = {
            'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
            'format': 'best',
            'noplaylist': True,
            'http_headers': { 'User-Agent': random_ua },
            'extractor_args': { 'youtube': { 'player_client': ['android', 'web'] }}
        }

        filename = ""
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            filename = ydl.prepare_filename(info)

        @after_this_request
        def remove_file(response):
            try: pass 
            except: pass
            return response

        return send_file(filename, as_attachment=True)

    except Exception as e:
        return f"Download Failed: {str(e)}"

def cleanup_downloads():
    try:
        now = time.time()
        for f in glob.glob(os.path.join(DOWNLOAD_FOLDER, "*")):
            if os.stat(f).st_mtime < now - 600:
                os.remove(f)
    except: pass

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    
