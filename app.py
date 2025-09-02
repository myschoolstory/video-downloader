import os
import shlex
import subprocess
import tempfile
import time
from pathlib import Path

import gradio as gr

OUTPUT_DIR = Path("/tmp/yt_downloader_outputs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def build_yt_dlp_cmd(url: str, target_format: str, quality: str, use_browser_cookies: bool, cookies_path: str, advanced: str):
    # Start base command
    cmd = ["yt-dlp", url, "-o", str(OUTPUT_DIR / "%(title)s.%(ext)s")]

    # Handle cookie options
    if cookies_path:
        cmd += ["--cookies", cookies_path]
    elif use_browser_cookies:
        # Try to use cookies from common browsers via yt-dlp helper
        # 'auto' lets yt-dlp choose an available browser
        cmd += ["--cookies-from-browser", "chrome"]

    # Handle format selection
    if target_format in {"mp3", "m4a", "wav"}:
        # extract audio
        cmd += ["-x", "--audio-format", target_format]
    elif target_format in {"mp4", "webm"}:
        # choose a video+audio format combination, restricting by height if quality is numeric
        if quality == "best":
            fmt = "bestvideo+bestaudio/best"
        else:
            # quality like '2160','1440','1080','720','480','360'
            try:
                h = int(quality)
                fmt = f"bestvideo[height<={h}]+bestaudio/best[height<={h}]"
            except Exception:
                fmt = "bestvideo+bestaudio/best"
        cmd += ["-f", fmt, "--merge-output-format", target_format]

    # Apply some sensible defaults
    cmd += ["--embed-metadata", "--embed-thumbnail", "--no-warnings"]

    # Advanced user-provided options (raw)
    if advanced and advanced.strip():
        # split respecting quotes
        try:
            extra = shlex.split(advanced)
            cmd += extra
        except Exception:
            # fallback: naive split
            cmd += advanced.split()

    return cmd

def run_download(url: str, target_format: str, quality: str, auto_cookies: bool, cookies_file, advanced_opts: str):
    """
    Perform download and return path to a zip containing the resulting file(s) or an error string.
    """
    # Validate URL
    if not url or not url.strip():
        return None, "Please provide a URL."

    # Save uploaded cookies file if provided
    cookies_path = ""
    if cookies_file is not None:
        # cookies_file is a tempfile-like object with a 'name' attribute or tuple (name, file)
        try:
            # gradio provides a dict-like object for files on some setups; handle common cases
            if isinstance(cookies_file, tuple) and len(cookies_file) >= 2:
                fp = cookies_file[1]
            else:
                fp = cookies_file
            dest = OUTPUT_DIR / f"cookies_{int(time.time())}.txt"
            with open(dest, "wb") as out_f, open(fp.name, "rb") as in_f:
                out_f.write(in_f.read())
            cookies_path = str(dest)
        except Exception as e:
            return None, f"Failed to save uploaded cookies file: {e}"

    cmd = build_yt_dlp_cmd(url, target_format, quality, auto_cookies, cookies_path, advanced_opts)

    # Run yt-dlp
    run_id = int(time.time())
    log_file = OUTPUT_DIR / f"yt-dlp-{run_id}.log"
    try:
        with open(log_file, "wb") as lf:
            proc = subprocess.run(cmd, stdout=lf, stderr=lf, check=False, timeout=1800)
    except subprocess.TimeoutExpired:
        return None, "Download timed out after 30 minutes."
    except FileNotFoundError:
        return None, "yt-dlp binary not found. Make sure yt-dlp is installed in the environment (see README)."


    # Inspect OUTPUT_DIR for files produced by this run (newer than when we started)
    results = []
    for p in OUTPUT_DIR.iterdir():
        # skip logs and cookies
        if p.suffix in {".log"} or p.name.startswith("cookies_"):
            continue
        # pick files created in the last hour to avoid old leftovers
        try:
            if time.time() - p.stat().st_mtime < 3600:
                results.append(p)
        except FileNotFoundError:
            continue

    if not results:
        # return the log as error message
        try:
            with open(log_file, "r", errors="ignore") as f:
                log_text = f.read()[:8000]
            return None, "No output files were produced. See log:\\n\\n" + log_text
        except Exception:
            return None, "No output files were produced; check server logs."

    # If we have results, create a zip to return via Gradio
    zip_path = OUTPUT_DIR / f"yt-dl-results-{run_id}.zip"
    import zipfile
    with zipfile.ZipFile(zip_path, "w") as zf:
        for p in results:
            zf.write(p, arcname=p.name)

    return str(zip_path), "Download completed successfully."


title = "Universal Video Downloader — yt-dlp + Gradio"
description = """
Download videos from YouTube, TikTok, Vimeo, Reddit and more using yt-dlp.
Supports output formats: mp4, webm (video), mp3, m4a, wav (audio).
Options:
 - Auto-grab cookies from local browser (for age-restricted/private videos)
 - Upload a cookies.txt file (Netscape cookie format)
 - Advanced options: raw yt-dlp arguments
"""

with gr.Blocks(title=title) as demo:
    gr.Markdown(f"# {title}")
    gr.Markdown(description)

    with gr.Row():
        url_in = gr.Textbox(label="Video URL", placeholder="https://youtube.com/watch?v=...")
        format_sel = gr.Dropdown(choices=["mp4","webm","mp3","m4a","wav"], value="mp4", label="Output format")

    with gr.Row():
        quality = gr.Dropdown(choices=["best","2160","1440","1080","720","480","360"], value="best", label="Max quality (height px)")
        auto_cookies = gr.Checkbox(label="Auto-grab cookies from browser (try chrome)", value=True)
        cookies_file = gr.File(label="Or upload cookies.txt (Netscape format)", file_count="single")

    advanced_opts = gr.Textbox(label="Advanced yt-dlp options (raw)", placeholder='e.g. --playlist-items 1-3 --no-check-certificate', lines=2)

    download_btn = gr.Button("Download")
    status = gr.Textbox(label="Status", interactive=False)
    result_file = gr.File(label="Result (zip)", interactive=False)

    def on_download(url, fmt, q, ac, cf, adv):
        status.value = "Starting..."
        result, msg = run_download(url, fmt, q, ac, cf, adv)
        status.value = msg
        if result:
            return gr.update(value=result), status.value
        else:
            return None, status.value

    download_btn.click(on_download, inputs=[url_in, format_sel, quality, auto_cookies, cookies_file, advanced_opts], outputs=[result_file, status])

if __name__ == '__main__':
    demo.launch(server_name='0.0.0.0', server_port=7860)
