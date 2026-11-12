"""
Antigravity ClipStudio - Lightweight Video Proxy, Hover Scrubbing GIF & 2GB Cache Manager (`proxy_manager.py`)
Implements:
1. Video Editing Proxies (360p / 480p Fast GOP Ultrafast MP4):
   - Generates lightweight proxy files for full-length masters and sliced clips, enabling instant scrubbing on iPhone, mobile Safari, and desktop without buffer stalls.
2. Dynamic Scrub Previews (6fps Animated Scrubbing GIFs):
   - Slices 10-60 frames across a clip into a responsive preview GIF for instantaneous timeline and card hover previewing.
3. Strict 2GB LRU (Least-Recently-Used) Disk Budget:
   - Tracks proxy and thumbnail file access times; when the proxy cache exceeds 2048 MB (2 GB), automatically evicts the oldest unviewed proxies to save local storage.
4. Thumbnail Generator:
   - Extracts frame-accurate JPEG/PNG posters at 2.0s or custom timestamps for Google Drive video libraries and UI cards.
"""

import os
import time
import subprocess
from pathlib import Path
from datetime import datetime

BASE_DIR = Path("/home/antigravity/video_editor_system")
CACHE_DIR = BASE_DIR / "cache"
PROXIES_DIR = CACHE_DIR / "proxies"
THUMBNAILS_DIR = BASE_DIR / "web" / "thumbnails"

PROXIES_DIR.mkdir(parents=True, exist_ok=True)
THUMBNAILS_DIR.mkdir(parents=True, exist_ok=True)

MAX_PROXY_CACHE_BYTES = 2 * 1024 * 1024 * 1024  # 2 GB limit


def get_proxy_cache_usage_bytes() -> int:
    """Returns total size of all files inside the proxies directory."""
    total = 0
    for p in PROXIES_DIR.glob("**/*"):
        if p.is_file():
            total += p.stat().st_size
    return total


def enforce_2gb_lru_budget():
    """
    Evicts the oldest least-recently-accessed proxies if total cache exceeds 2 GB.
    Returns list of deleted file paths.
    """
    total = get_proxy_cache_usage_bytes()
    evicted = []
    if total <= MAX_PROXY_CACHE_BYTES:
        return evicted

    # Gather all proxy files sorted by access time (oldest first)
    files = [f for f in PROXIES_DIR.glob("**/*") if f.is_file()]
    files.sort(key=lambda f: f.stat().st_atime)

    for f in files:
        if total <= (MAX_PROXY_CACHE_BYTES * 0.85):  # Evict down to 85% watermark
            break
        sz = f.stat().st_size
        try:
            f.unlink()
            total -= sz
            evicted.append({"path": str(f), "freed_bytes": sz})
        except OSError:
            pass
    return evicted


def generate_video_proxy(source_path: Path, output_name: str = None, target_height: int = 360) -> dict:
    """
    Generates a 360p lightweight scrubbing proxy video with 15-frame GOP keyframes
    for instantaneous scrub seeking on iPhone/Mac web browsers.
    """
    if not source_path.exists():
        return {"ok": False, "error": "Source file not found"}

    if output_name is None:
        output_name = f"{source_path.stem}_proxy_{target_height}p.mp4"

    out_file = PROXIES_DIR / output_name
    if out_file.exists():
        # Update atime
        os.utime(out_file, None)
        return {
            "ok": True,
            "cached": True,
            "proxy_path": str(out_file),
            "size_bytes": out_file.stat().st_size,
            "url": f"/media/proxies/{out_file.name}"
        }

    # Generate 360p fast-seek proxy
    cmd = [
        "ffmpeg", "-y", "-hide_banner",
        "-i", str(source_path),
        "-vf", f"scale=-2:{target_height}",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "28",
        "-g", "15", "-keyint_min", "15", "-sc_threshold", "0",
        "-c:a", "aac", "-b:a", "64k",
        "-movflags", "+faststart",
        str(out_file)
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if res.returncode == 0 and out_file.exists():
        enforce_2gb_lru_budget()
        return {
            "ok": True,
            "cached": False,
            "proxy_path": str(out_file),
            "size_bytes": out_file.stat().st_size,
            "url": f"/media/proxies/{out_file.name}"
        }
    return {"ok": False, "error": res.stderr.decode("utf-8", errors="replace")}


def generate_scrubbing_gif(source_path: Path, output_name: str = None, start_sec: float = 1.0, duration_sec: float = 4.0) -> dict:
    """Generates a smooth 6fps animated preview GIF for hover scrubbing."""
    if not source_path.exists():
        return {"ok": False, "error": "Source file not found"}

    if output_name is None:
        output_name = f"{source_path.stem}_scrub.gif"

    out_file = THUMBNAILS_DIR / output_name
    if out_file.exists():
        return {"ok": True, "cached": True, "url": f"/thumbnails/{out_file.name}"}

    cmd = [
        "ffmpeg", "-y", "-hide_banner",
        "-ss", str(start_sec), "-t", str(duration_sec),
        "-i", str(source_path),
        "-vf", "fps=6,scale=320:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse",
        str(out_file)
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if res.returncode == 0 and out_file.exists():
        return {"ok": True, "cached": False, "url": f"/thumbnails/{out_file.name}"}
    return {"ok": False, "error": res.stderr.decode("utf-8", errors="replace")}


def generate_video_poster(source_path: Path, output_name: str = None, timestamp_sec: float = 2.0) -> dict:
    """Extracts a frame-accurate JPEG poster thumbnail."""
    if not source_path.exists():
        return {"ok": False, "error": "Source file not found"}

    if output_name is None:
        output_name = f"{source_path.stem}.jpg"

    out_file = THUMBNAILS_DIR / output_name
    if out_file.exists():
        return {"ok": True, "cached": True, "url": f"/thumbnails/{out_file.name}"}

    cmd = [
        "ffmpeg", "-y", "-hide_banner",
        "-ss", str(timestamp_sec),
        "-i", str(source_path),
        "-vframes", "1", "-q:v", "3",
        "-vf", "scale=480:-1",
        str(out_file)
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if res.returncode == 0 and out_file.exists():
        return {"ok": True, "cached": False, "url": f"/thumbnails/{out_file.name}"}
    return {"ok": False, "error": res.stderr.decode("utf-8", errors="replace")}


if __name__ == "__main__":
    # Test proxy generation for real 87MB master
    master = CACHE_DIR / "adhd_timers_playable_master.mp4"
    if master.exists():
        p_res = generate_video_proxy(master, "master_adhd_timers_proxy_360p.mp4")
        g_res = generate_scrubbing_gif(master, "master_adhd_timers_scrub.gif", 74.0, 5.0)
        t_res = generate_video_poster(master, "master_adhd_timers.jpg", 75.0)
        print("Master Proxy:", p_res)
        print("Master Scrub GIF:", g_res)
        print("Master Poster:", t_res)
    print("Proxy cache usage:", round(get_proxy_cache_usage_bytes() / (1024 * 1024), 2), "MB / 2048 MB")
