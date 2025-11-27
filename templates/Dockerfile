FROM python:3.9-slim

# Install FFmpeg (Required for processing)
RUN apt-get update && apt-get install -y ffmpeg

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

CMD ["gunicorn", "app:app", "-b", "0.0.0.0:8000"]
