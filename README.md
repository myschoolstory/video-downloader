# Universal Video Downloader (yt-dlp + Gradio)

This project provides a simple Gradio web UI to download videos/audio from YouTube, TikTok, Vimeo, Reddit and many other platforms using `yt-dlp`.

## Features
- Output formats: `mp4`, `webm`, `mp3`, `m4a`, `wav`
- Quality selection: best, 2160, 1440, 1080, 720, 480, 360
- Auto-grab cookies from a local browser (via yt-dlp's `--cookies-from-browser`)
- Upload a `cookies.txt` (Netscape format) file
- Advanced options: pass raw `yt-dlp` args

## Usage

### Local
1. Install dependencies:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Run:
```bash
python app.py
```

Open http://localhost:7860

### Docker
Build and run:
```bash
docker build -t yt-gradio-downloader .
docker run -p 7860:7860 yt-gradio-downloader
```

### Notes & Security
- `--cookies-from-browser` only works if the container has access to the host's browser profiles (commonly not the case in Docker). For server deployments, prefer uploading a `cookies.txt` exported from your browser.
- Downloading copyrighted content may violate the platform's Terms of Service or copyright law in your jurisdiction. Use responsibly.
- This app executes `yt-dlp` subprocesses -- never run untrusted inputs on a public server.

### Integration Coming Soon
I will soon integrate this with a library I'm working on to automatically grab cookies from websites. For now, you have to manually get cookies, or allow it to grab them from chrome on your device.

