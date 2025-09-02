# Universal Video Downloader (yt-dlp + Gradio)

This project provides a simple Gradio web UI to download videos/audio from YouTube, TikTok, Vimeo, Reddit and many other platforms using `yt-dlp`.

## Features
- Output formats: `mp4`, `webm`, `mp3`, `m4a`, `wav`
- Quality selection: best, 2160, 1440, 1080, 720, 480, 360
- Auto-grab cookies from a local browser (via yt-dlp's `--cookies-from-browser`)
- Upload a `cookies.txt` (Netscape format) file
- **Generate fresh cookies** by automatically visiting websites before download
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

## Cookie Management

This application offers three methods for handling cookies to access restricted content:

### 1. Browser Cookie Extraction
- Uses yt-dlp's `--cookies-from-browser` feature
- Extracts cookies from your local browser (Chrome, Firefox, etc.)
- **Best for**: Local usage where you're already logged into sites
- **Limitations**: Doesn't work in Docker containers without special configuration

### 2. Cookie File Upload
- Upload a `cookies.txt` file in Netscape format
- Export cookies from your browser using extensions like "Get cookies.txt"
- **Best for**: Server deployments and when you have pre-exported cookies
- **Limitations**: Cookies may expire and need manual updates

### 3. Fresh Cookie Generation (New!)
- Automatically visits the target website to collect fresh cookies
- Uses the integrated cookie-creator utility
- **Best for**: Accessing sites that require fresh session cookies or when existing cookies are expired
- **Benefits**: 
  - No need to manually export cookies
  - Works in any environment with internet access
  - Automatically handles cookie collection and formatting
- **Requirements**: The application needs network access to visit the target site

#### When to Use Fresh Cookie Generation
- When downloads fail with "Video unavailable" or authentication errors
- For sites that frequently expire cookies or require fresh sessions
- When you don't have browser access or can't export cookies manually
- For automated workflows where manual cookie management isn't practical

#### How It Works
1. Check "Generate fresh cookies (visit site first)" in the interface
2. The application visits the target URL using a web browser simulation
3. Cookies are automatically collected and saved in yt-dlp compatible format
4. The download proceeds using the fresh cookies
5. Temporary cookie files are cleaned up after download

### Notes & Security
- `--cookies-from-browser` only works if the container has access to the host's browser profiles (commonly not the case in Docker). For server deployments, prefer uploading a `cookies.txt` or using fresh cookie generation.
- Fresh cookie generation requires network access to visit target sites
- Downloading copyrighted content may violate the platform's Terms of Service or copyright law in your jurisdiction. Use responsibly.
- This app executes `yt-dlp` subprocesses -- never run untrusted inputs on a public server.
- Cookie files contain sensitive session information - they are automatically cleaned up but ensure your deployment is secure.

## Troubleshooting

### Cookie-Related Issues

**Download fails with "Video unavailable" or "Private video":**
1. Try the "Generate fresh cookies" option first
2. If that fails, try browser cookie extraction
3. As a last resort, manually export cookies from your browser and upload the file

**Fresh cookie generation fails:**
- Check your internet connection
- Ensure the target site is accessible from your network
- Some sites may block automated access - try browser cookie extraction instead
- Check the console output for specific error messages

**Browser cookie extraction not working:**
- Ensure you're logged into the target site in your browser
- Try a different browser (Chrome, Firefox, Edge)
- In Docker environments, this feature typically won't work

**Cookies expire quickly:**
- Use fresh cookie generation for sites with short-lived sessions
- Some platforms expire cookies within hours - regenerate as needed

### Network Issues

**Connection timeouts during cookie generation:**
- Check if the target site is accessible
- Some corporate networks may block certain domains
- Try using a VPN if the site is geo-restricted

**SSL/Certificate errors:**
- Ensure your system's certificates are up to date
- Some sites may have certificate issues that prevent automated access

### General Download Issues

**Format not available:**
- Try different quality settings
- Some content may only be available in specific formats
- Check if the content is geo-restricted

**Slow downloads:**
- This is typically due to the source site's bandwidth limitations
- yt-dlp will automatically retry failed downloads

For more detailed troubleshooting, check the console output for specific error messages from yt-dlp.

