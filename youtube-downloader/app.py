"""YouTube Downloader – kleine lokale Web-App auf Basis von yt-dlp.

Start:  python app.py   →  http://127.0.0.1:5000
"""
from __future__ import annotations

import os
import shutil
import threading
import uuid
import webbrowser
from pathlib import Path

from flask import Flask, abort, jsonify, request, send_file, send_from_directory
import yt_dlp

BASE_DIR = Path(__file__).resolve().parent
DOWNLOAD_DIR = Path(os.environ.get("YTDL_DIR", BASE_DIR / "downloads"))
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)


def find_ffmpeg() -> str | None:
    """System-ffmpeg bevorzugen, sonst das von imageio-ffmpeg mitgelieferte."""
    path = shutil.which("ffmpeg")
    if path:
        return path
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return None


FFMPEG = find_ffmpeg()
app = Flask(__name__, static_folder=str(BASE_DIR / "static"))
jobs: dict[str, dict] = {}
jobs_lock = threading.Lock()


def base_opts() -> dict:
    opts = {"quiet": True, "no_warnings": True, "noplaylist": True}
    if FFMPEG:
        opts["ffmpeg_location"] = FFMPEG
    return opts


@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.post("/api/info")
def info():
    url = (request.get_json(silent=True) or {}).get("url", "").strip()
    if not url:
        return jsonify(error="Bitte einen Link eingeben."), 400
    try:
        with yt_dlp.YoutubeDL(base_opts()) as ydl:
            data = ydl.extract_info(url, download=False)
    except Exception as exc:  # yt-dlp wirft viele verschiedene Fehler
        return jsonify(error=f"Video konnte nicht geladen werden: {exc}"), 400

    heights = sorted(
        {f["height"] for f in data.get("formats", []) if f.get("height") and f.get("vcodec") != "none"},
        reverse=True,
    )
    return jsonify(
        title=data.get("title"),
        uploader=data.get("uploader"),
        duration=data.get("duration"),
        thumbnail=data.get("thumbnail"),
        heights=heights,
        ffmpeg=bool(FFMPEG),
    )


def run_job(job_id: str, url: str, mode: str, quality: int | None) -> None:
    job = jobs[job_id]

    def hook(d):
        if d["status"] == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            job["percent"] = round(d.get("downloaded_bytes", 0) / total * 100, 1) if total else None
            job["speed"] = d.get("_speed_str", "").strip()
            job["eta"] = d.get("_eta_str", "").strip()
            job["state"] = "downloading"
        elif d["status"] == "finished":
            job["state"] = "processing"

    opts = base_opts() | {
        "outtmpl": str(DOWNLOAD_DIR / "%(title).150B [%(id)s].%(ext)s"),
        "progress_hooks": [hook],
        "windowsfilenames": True,
    }
    if mode == "audio":
        opts["format"] = "bestaudio/best"
        if FFMPEG:
            opts["postprocessors"] = [
                {"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}
            ]
    else:
        h = f"[height<={quality}]" if quality else ""
        if FFMPEG:
            opts["format"] = f"bv*{h}[ext=mp4]+ba[ext=m4a]/bv*{h}+ba/b{h}/b"
            opts["merge_output_format"] = "mp4"
        else:  # ohne ffmpeg nur Formate, die Bild+Ton schon enthalten
            opts["format"] = f"b{h}[acodec!=none][vcodec!=none]/b"

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            data = ydl.extract_info(url, download=True)
        downloads = data.get("requested_downloads") or []
        path = downloads[0].get("filepath") if downloads else ydl.prepare_filename(data)
        job.update(state="done", percent=100, file=path, name=Path(path).name)
    except Exception as exc:
        job.update(state="error", error=str(exc))


@app.post("/api/download")
def download():
    body = request.get_json(silent=True) or {}
    url = body.get("url", "").strip()
    mode = "audio" if body.get("mode") == "audio" else "video"
    quality = body.get("quality")
    quality = int(quality) if str(quality or "").isdigit() else None
    if not url:
        return jsonify(error="Bitte einen Link eingeben."), 400

    job_id = uuid.uuid4().hex
    with jobs_lock:
        jobs[job_id] = {"state": "queued", "percent": 0}
    threading.Thread(target=run_job, args=(job_id, url, mode, quality), daemon=True).start()
    return jsonify(id=job_id)


@app.get("/api/status/<job_id>")
def status(job_id: str):
    job = jobs.get(job_id) or abort(404)
    return jsonify({k: v for k, v in job.items() if k != "file"})


@app.get("/api/file/<job_id>")
def file(job_id: str):
    job = jobs.get(job_id)
    if not job or job.get("state") != "done":
        abort(404)
    return send_file(job["file"], as_attachment=True, download_name=job["name"])


if __name__ == "__main__":
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "5000"))
    print(f"YouTube Downloader läuft auf http://{host}:{port}  (Dateien in {DOWNLOAD_DIR})")
    if not FFMPEG:
        print("Hinweis: ffmpeg nicht gefunden – MP3 und hohe Auflösungen sind nicht verfügbar.")
    if os.environ.get("NO_BROWSER") != "1":
        threading.Timer(1.0, lambda: webbrowser.open(f"http://{host}:{port}")).start()
    app.run(host=host, port=port, debug=False)
