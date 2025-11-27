from flask import Flask, render_template, request, send_file, after_this_request
import yt_dlp
import os
import glob
import time
from fake_useragent import UserAgent

app = Flask(__name__)

# Create download directory
DOWNLOAD_FOLDER = 'downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_video():
    video_url = request.form['url']
    
    # 1. Generate a Fake User Identity (Stealth Mode)
    # This makes the server look like a random phone/laptop
    ua = UserAgent()
    random_ua = ua.random
    
    print(f"Processing: {video_url}")
    print(f"Using Identity: {random_ua}")

    try:
        # Clean up old files (older than 10 mins) to save space
        cleanup_downloads()

        # 2. Configure the Engine
        ydl_opts = {
            'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
            'format': 'best',  # Simplest format (less likely to error)
            'noplaylist': True,
            
            # STEALTH SETTINGS
            'http_headers': {
                'User-Agent': random_ua,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
            },
            # Force IPv4 (more stable on Render)
            'source_address': '0.0.0.0', 
            
            # Instagram Specific Fixes
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'web']
                }
            }
        }

        filename = ""
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            filename = ydl.prepare_filename(info)

        # 3. Send file to user
        @after_this_request
        def remove_file(response):
            try:
                # Wait a tiny bit then delete (save space)
                # os.remove(filename) 
                pass 
            except Exception as error:
                print(f"Error removing file: {error}")
            return response

        return send_file(filename, as_attachment=True)

    except Exception as e:
        error_msg = str(e)
        if "Sign in" in error_msg:
            return "Error: This video requires a login (YouTube Block). Try Instagram!"
        return f"Download Failed: {error_msg}"

def cleanup_downloads():
    try:
        now = time.time()
        for f in glob.glob(os.path.join(DOWNLOAD_FOLDER, "*")):
            if os.stat(f).st_mtime < now - 600: # 10 mins
                os.remove(f)
    except:
        pass

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    
