"""
Antigravity ClipStudio - Source Videos Hierarchy Manager (`source_videos_manager.py`)
Manages the canonical Google Drive folder structure:
- Root: `Source Videos [Clipstudio]` (`1PLLjdQtqU9JxdVWsbXJZ5N5z6lSpNqwW`)
  - `Full Videos` (`1Fg1MkNaxC5m7Fqzi_-RSZled2ymxkCvk`)
    - `<Video Title>` Folder (e.g., `3 Epic ADHD Timers _ go take ur adderall before watching this`, ID: `1kX2lDJC6I306sqT79QbBmINNcSP_7rQN`)
      - Master Video File (`<Video Title>.mp4`, e.g., `1gGjzFKXmDSS_dR0aCzlF84M4TvZTIvl8`)
      - `takes_packed.md` (Immutable phrase-indexed transcript + silence map)
      - `edl_storyboard.json` (Edit Decision List for this source video)
      - `Clips/` Subfolder (e.g., `1dzQaejxrM3Y6Gqe58BazhdsEq5PdMPai`)
        - `<clip_id>_16x9.mp4`
        - `<clip_id>_9x16_short.mp4`
"""

import os
import re
import json
import subprocess
from pathlib import Path
from datetime import datetime

BASE_DIR = Path("/home/antigravity/video_editor_system")
CACHE_DIR = BASE_DIR / "cache"
CLIPS_CACHE_DIR = CACHE_DIR / "clips"
TRANSCRIPTS_CACHE_DIR = CACHE_DIR / "transcripts"
PROFILES_DIR = BASE_DIR / "profiles"

SOURCE_VIDEOS_ROOT_ID = "1PLLjdQtqU9JxdVWsbXJZ5N5z6lSpNqwW"
FULL_VIDEOS_FOLDER_ID = "1Fg1MkNaxC5m7Fqzi_-RSZled2ymxkCvk"
CLIPSTUDIO_ROOT_ID = "17N2FTWKILTfObOIkrJTfAslILQyzFs9e"
CLIPSTUDIO_SETTINGS_ID = "1cghO_UEYcRGBDmuLIbeE7xcaXBebBEBd"

# Known canonical folder for "3 Epic ADHD Timers"
ADHD_TIMERS_FOLDER_ID = "1kX2lDJC6I306sqT79QbBmINNcSP_7rQN"
ADHD_TIMERS_VIDEO_FILE_ID = "1gGjzFKXmDSS_dR0aCzlF84M4TvZTIvl8"
ADHD_TIMERS_CLIPS_FOLDER_ID = "1dzQaejxrM3Y6Gqe58BazhdsEq5PdMPai"

SOURCE_REGISTRY_FILE = PROFILES_DIR / "source_videos_registry.json"


def _run_gdrive(args):
    env = os.environ.copy()
    env["ANTIGRAVITY_APP_DATA_DIR"] = "/tmp/antigravity"
    cmd = ["/opt/antigravity/bin/gdrive"] + args
    res = subprocess.run(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return res.returncode, res.stdout, res.stderr


def parse_gdrive_ls(output: str):
    lines = [line.strip() for line in output.strip().splitlines() if line.strip()]
    items = []
    for line in lines[2:]:  # skip header and separator
        parts = re.split(r"\s{2,}", line)
        if len(parts) >= 3:
            items.append({
                "id": parts[0].strip(),
                "name": parts[1].strip(),
                "type": parts[2].strip(),
                "size": parts[3].strip() if len(parts) >= 4 else "0 B"
            })
    return items


def scan_source_videos_hierarchy():
    """
    Scans `Source Videos [Clipstudio]` -> `Full Videos` -> `<Video Title>` folders,
    mapping each video folder's master video file, `Clips` subfolder, and generated clips.
    """
    code, out, _ = _run_gdrive(["readonly", "ls", FULL_VIDEOS_FOLDER_ID])
    video_folders = parse_gdrive_ls(out) if code == 0 else []

    catalog = []
    for vf in video_folders:
        if vf["type"] != "folder":
            continue
        vf_id = vf["id"]
        vf_name = vf["name"]
        c2, out2, _ = _run_gdrive(["readonly", "ls", vf_id])
        children = parse_gdrive_ls(out2) if c2 == 0 else []

        master_video = None
        clips_folder = None
        transcript_file = None
        other_files = []

        for child in children:
            cname_lower = child["name"].lower()
            if child["type"] == "folder" and cname_lower == "clips":
                clips_folder = child
            elif "video/" in child["type"] or cname_lower.endswith((".mp4", ".mov", ".mkv", ".webm")):
                master_video = child
            elif cname_lower.endswith(".md") or "transcript" in cname_lower or "packed" in cname_lower:
                transcript_file = child
            else:
                other_files.append(child)

        # List existing clips inside the `Clips` subfolder
        clips_list = []
        if clips_folder:
            c3, out3, _ = _run_gdrive(["readonly", "ls", clips_folder["id"]])
            clips_list = parse_gdrive_ls(out3) if c3 == 0 else []

        catalog.append({
            "video_folder_id": vf_id,
            "video_title": vf_name,
            "master_video": master_video,
            "clips_folder": clips_folder,
            "transcript_file": transcript_file,
            "clips": clips_list,
            "other_files": other_files
        })

    registry = {
        "scanned_at": datetime.utcnow().isoformat() + "Z",
        "source_videos_root_id": SOURCE_VIDEOS_ROOT_ID,
        "full_videos_folder_id": FULL_VIDEOS_FOLDER_ID,
        "total_source_video_folders": len(catalog),
        "source_videos": catalog
    }
    PROFILES_DIR.mkdir(parents=True, exist_ok=True)
    with open(SOURCE_REGISTRY_FILE, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2)
    return registry


def upload_file_to_drive_folder(local_path: Path, parent_folder_id: str):
    """Uploads a local file into the specified Google Drive parent folder."""
    code, out, err = _run_gdrive(["mutate", "upload", str(local_path), "--parent", parent_folder_id])
    file_id = None
    for line in out.splitlines():
        if line.strip().startswith("Id:") or "id" in line.lower():
            parts = line.split(":", 1)
            if len(parts) == 2:
                file_id = parts[1].strip()
    return {
        "ok": code == 0,
        "file_id": file_id,
        "stdout": out.strip(),
        "stderr": err.strip()
    }


def create_video_source_folder_structure(video_title: str):
    """
    Creates the canonical `<Video Title>` folder inside `Full Videos` (`1Fg1MkNaxC5m7Fqzi_-RSZled2ymxkCvk`)
    and creates a `Clips` subfolder inside `<Video Title>`.
    """
    c1, out1, err1 = _run_gdrive(["mutate", "mkdir", video_title, "--parent", FULL_VIDEOS_FOLDER_ID])
    video_folder_id = None
    for line in out1.splitlines():
        if "id" in line.lower() and ":" in line:
            video_folder_id = line.split(":", 1)[1].strip()

    clips_folder_id = None
    if video_folder_id:
        c2, out2, _ = _run_gdrive(["mutate", "mkdir", "Clips", "--parent", video_folder_id])
        for line in out2.splitlines():
            if "id" in line.lower() and ":" in line:
                clips_folder_id = line.split(":", 1)[1].strip()

    return {
        "video_title": video_title,
        "video_folder_id": video_folder_id,
        "clips_folder_id": clips_folder_id,
        "stdout": out1.strip(),
        "stderr": err1.strip()
    }


if __name__ == "__main__":
    reg = scan_source_videos_hierarchy()
    print(json.dumps(reg, indent=2))
