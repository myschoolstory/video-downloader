# Dockerfile for yt-dlp + Gradio downloader
FROM python:3.11-slim

# Install system dependencies (ffmpeg, fonts if needed, and common libs)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    ca-certificates \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy files
COPY requirements.txt /app/requirements.txt
COPY cookie-creator/ /app/cookie-creator/
COPY app.py /app/app.py
COPY README.md /app/README.md

# Install Python deps
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r /app/requirements.txt

# Expose port for Gradio
ENV PORT=7860
EXPOSE 7860

# Run the app
CMD ["python", "app.py"]
