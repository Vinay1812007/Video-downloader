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

# NEW LIST: INVIDIOUS SERVERS (More stable than Piped)
# These servers proxy the video for you.
INVIDIOUS_SERVERS = [
    "https://inv.nadeko.net",          # Very Fast
    "https://invidious.drgns.space",   # Reliable
    "https://yewtu.be",                # The Original (Netherlands)
    "https://invidious.flokinet.to",   # Secure
    "https://vid.puffyan.us",          # Backup
    "https://inv.tux.pizza"            # Backup
]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_video():
    video_url = request.form['url']
    
    # 1. YOUTUBE HANDLER (Using Invidious API)
    if "youtube.com" in video_url or "youtu.be" in video_url:
        return download_youtube_invidious(video_url)

    # 2. INSTAGRAM/TIKTOK HANDLER (Your working Stealth Mode)
    return download_standard(video_url)

def download_youtube_invidious(url):
    """
    Uses Invidious API to find a direct video stream.
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
            return "Error: Could not find YouTube Video ID."

        print(f"YouTube ID: {video_id}. Switching to Invidious Network...")

        # Loop through Invidious servers
        for api_base in INVIDIOUS_SERVERS:
            try:
                # API Call to get video details
                print(f"Checking {api_base}...")
                api_url = f"{api_base}/api/v1/videos/{video_id}"
                resp = requests.get(api_url, timeout=10)
                
                if resp.status_code == 200:
                    data = resp.json()
                    
                    # 1. Try to find a nice MP4 (720p or 360p)
                    for stream in data.get('formatStreams', []):
                        # Look for mp4 with audio
                        if stream['container'] == 'mp4' and 'resolution' in stream:
                            # Verify resolution is good (not 144p)
                            if '720p' in stream['resolution'] or '360p' in stream['resolution']:
                                print(f"Found stream on {api_base}")
                                return redirect(stream['url'])
                                
                    # 2. If no formatStreams, try the "Latest Version" shortcut
                    # This is a special link that forces a download
                    return redirect(f"{api_base}/latest_version?id={video_id}&itag=22")

            except Exception as e:
                print(f"Server {api_base} failed: {e}")
                continue 

        # FAIL-SAFE: If APIs fail, send to the "Yewtu.be" watch page
        # This page usually works even when APIs are strict
        return redirect(f"https://yewtu.be/watch?v={video_id}")

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
