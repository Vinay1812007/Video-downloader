from flask import Flask, render_template, request, send_file, redirect, after_this_request
import yt_dlp
import os
import glob
import time
import requests
from fake_useragent import UserAgent

app = Flask(__name__)

DOWNLOAD_FOLDER = 'downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# LIST OF PUBLIC YOUTUBE PROXIES (Piped API)
# These bypass the "Sign In" block
PIPED_SERVERS = [
    "https://pipedapi.kavin.rocks",
    "https://api.piped.privacy.com.de",
    "https://pipedapi.drgns.space",
    "https://api.piped.sakurajima.moe"
]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_video():
    video_url = request.form['url']
    
    # 1. SPECIAL HANDLER FOR YOUTUBE
    # Render servers are blocked by YouTube, so we use Piped API instead.
    if "youtube.com" in video_url or "youtu.be" in video_url:
        return download_youtube_via_proxy(video_url)

    # 2. STANDARD HANDLER (Instagram, TikTok, Twitter)
    # This uses the "Stealth Mode" engine that is already working for you.
    return download_standard(video_url)

def download_youtube_via_proxy(url):
    """Fallback method using Piped API for YouTube"""
    try:
        # Extract Video ID
        video_id = ""
        if "youtu.be" in url:
            video_id = url.split("/")[-1].split("?")[0]
        elif "v=" in url:
            video_id = url.split("v=")[1].split("&")[0]
        elif "shorts" in url:
            video_id = url.split("shorts/")[1].split("?")[0]
            
        if not video_id:
            return "Error: Could not find YouTube Video ID."

        print(f"YouTube Detect (ID: {video_id}). Switching to Piped Network...")

        # Loop through Piped servers until one works
        for api_base in PIPED_SERVERS:
            try:
                # Get video stream data
                api_url = f"{api_base}/streams/{video_id}"
                resp = requests.get(api_url, timeout=10)
                
                if resp.status_code == 200:
                    data = resp.json()
                    # Find the best video stream (mp4)
                    for stream in data['videoStreams']:
                        if stream['format'] == 'MPEG-4' and stream['videoOnly'] == False:
                            # Found a working link! Redirect user directly to it.
                            return redirect(stream['url'])
            except:
                continue
        
        return "Error: YouTube servers are busy. Try Instagram for now."

    except Exception as e:
        return f"YouTube Error: {str(e)}"

def download_standard(url):
    """Standard yt-dlp engine for Instagram/Others"""
    ua = UserAgent()
    random_ua = ua.random
    
    print(f"Standard Download: {url} | Agent: {random_ua}")

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
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        @after_this_request
        def remove_file(response):
            try:
                # os.remove(filename) # Keep file for a bit
                pass
            except: pass
            return response

        return send_file(filename, as_attachment=True)

    except Exception as e:
        return f"Error: {str(e)}"

def cleanup_downloads():
    try:
        now = time.time()
        for f in glob.glob(os.path.join(DOWNLOAD_FOLDER, "*")):
            if os.stat(f).st_mtime < now - 600:
                os.remove(f)
    except: pass

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
