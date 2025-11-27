from flask import Flask, render_template, request, redirect, url_for, send_file
import yt_dlp
import os

app = Flask(__name__)

# Configure download folder
DOWNLOAD_FOLDER = 'downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_video():
    video_url = request.form['url']
    format_type = request.form['type'] # 'video' or 'audio'

    try:
        # Options for yt-dlp
        ydl_opts = {
            'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
            'format': 'bestvideo+bestaudio/best' if format_type == 'video' else 'bestaudio/best',
            'merge_output_format': 'mp4', # Ensures video is always MP4
        }
        
        if format_type == 'audio':
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            filename = ydl.prepare_filename(info)
            
            # Adjust filename extension if converted to mp3
            if format_type == 'audio':
                filename = filename.rsplit('.', 1)[0] + '.mp3'

        return send_file(filename, as_attachment=True)

    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
