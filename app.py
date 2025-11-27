from flask import Flask, render_template, request, send_file, redirect, after_this_request
import yt_dlp
import os
import glob
import time
import requests
import random
from fake_useragent import UserAgent

app = Flask(__name__)

DOWNLOAD_FOLDER = 'downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# MASSIVE LIST OF YOUTUBE PROXIES (Piped Network)
# If one is busy, we instantly try the next.
PIPED_SERVERS = [
    "https://pipedapi.kavin.rocks",          # Official (Fastest)
    "https://api.piped.privacy.com.de",      # Europe Strong
    "https://pipedapi.drgns.space",          # US Backup
    "https://api.piped.sakurajima.moe",      # Asia Backup
    "https://pipedapi.tokhmi.xyz",           # Reliable
    "https://api.piped.projectsegfau.lt",    # Secure
    "https://pipedapi.smnz.de",              # German Server
    "https://pipedapi.adminforge.de"         # Backup
]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_video():
    video_url = request.form['url']
    
    # 1. YOUTUBE HANDLER (Piped Proxy Network)
    if "youtube.com" in video_url or "youtu.be" in video_url:
        return download_youtube_via_proxy(video_url)

    # 2. INSTAGRAM/TIKTOK HANDLER (Stealth Mode)
    return download_standard(video_url)

def download_youtube_via_proxy(url):
    """
    Tries 8 different servers to find a working link.
    If all fail, sends user to a Watch Page (Fail-Safe).
    """
    try:
        # Extract Video ID safely
        video_id = ""
        if "youtu.be" in url:
            video_id = url.split("/")[-1].split("?")[0]
        elif "v=" in url:
            video_id = url.split("v=")[1].split("&")[0]
        elif "shorts" in url:
            video_id = url.split("shorts/")[1].split("?")[0]
            
        if not video_id:
            return "Error: Bad Link. Could not find Video ID."

        print(f"YouTube ID: {video_id}. Hunting for a working server...")

        # Loop through ALL servers in the list
        for api_base in PIPED_SERVERS:
            try:
                # Ask server for video info
                print(f"Trying {api_base}...")
                resp = requests.get(f"{api_base}/streams/{video_id}", timeout=6)
                
                if resp.status_code == 200:
                    data = resp.json()
                    # Look for the best MP4 stream
                    for stream in data['videoStreams']:
                        if stream['format'] == 'MPEG-4' and not stream['videoOnly']:
                            print(f"Success! Redirecting using {api_base}")
                            return redirect(stream['url'])
            except:
                continue # If this server fails, try the next one instantly

        # FAIL-SAFE: If ALL 8 servers fail, send user to a Piped Watch Page
        # They can watch/download manually from there.
        print("All APIs busy. Activating Fail-Safe.")
        return redirect(f"https://piped.video/watch?v={video_id}")

    except Exception as e:
        return f"System Error: {str(e)}"

def download_standard(url):
    """Standard Engine for Instagram (Works perfectly)"""
    ua = UserAgent()
    random_ua = ua.random
    
    print(f"Processing Insta/Other: {url}")

    try:
        cleanup_downloads()
        
        ydl_opts = {
            'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
            'format': 'best',
            'noplaylist': True,
            'http_headers': { 'User-Agent': random_ua },
            # Instagram Fixes
            'extractor_args': { 'youtube': { 'player_client': ['android', 'web'] }}
        }

        filename = ""
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        @after_this_request
        def remove_file(response):
            try:
                # os.remove(filename) 
                pass
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
