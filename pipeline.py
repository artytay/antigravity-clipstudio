"""
Auto-segmentation & Transcription Pipeline
1. Pulls YouTube transcript if available (instant, no GPU needed)
2. Falls back to audio extraction + whisper / Gemini transcription
3. Saves transcripts persistently as .transcript.json alongside video or in cache
4. Analyzes transcript text to auto-identify product segments with micro-second boundaries
"""

import os
import sys
import json
import re
import urllib.request
import urllib.parse
from pathlib import Path
from engine import (
    load_cached_transcript, 
    save_transcript_to_cache, 
    snap_timestamp_to_silence,
    slice_video,
    upload_clip_to_drive,
    DEFAULT_DRIVE_FOLDER_ID
)

def extract_youtube_video_id(url: str) -> str:
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        r'(?:youtu\.be\/)([0-9A-Za-z_-]{11})'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return "unknown_video"

def parse_time_str(val) -> float:
    if isinstance(val, (int, float)):
        return float(val)
    parts = str(val).strip().split(":")
    if len(parts) == 3:
        return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
    elif len(parts) == 2:
        return float(parts[0]) * 60 + float(parts[1])
    return float(val)

def format_time_code(seconds: float) -> str:
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    millis = int(round((seconds - int(seconds)) * 1000))
    hrs = mins // 60
    mins = mins % 60
    if hrs > 0:
        return f"{hrs:02d}:{mins:02d}:{secs:02d}.{millis:03d}"
    return f"{mins:02d}:{secs:02d}.{millis:03d}"

def auto_segment_transcript(transcript_items: list, keywords_config: list) -> list:
    """
    Given transcript cues [{'text': '...', 'start': 75.0, 'duration': 4.2}],
    searches for keyword anchors (e.g. ['cube timer', 'flip timer'], ['radial timer'])
    and constructs candidate clip segments with preliminary timestamps.
    """
    segments = []
    
    for product in keywords_config:
        name = product["name"]
        keywords = [k.lower() for k in product["keywords"]]
        
        matching_cues = []
        for idx, cue in enumerate(transcript_items):
            text_lower = cue["text"].lower()
            if any(k in text_lower for k in keywords):
                matching_cues.append(idx)
                
        if not matching_cues:
            continue
            
        # Group contiguous or closely spaced mentions (within 45s of each other)
        groups = []
        current_group = [matching_cues[0]]
        for idx in matching_cues[1:]:
            prev_cue = transcript_items[current_group[-1]]
            this_cue = transcript_items[idx]
            if (this_cue["start"] - (prev_cue["start"] + prev_cue.get("duration", 2))) < 45.0:
                current_group.append(idx)
            else:
                groups.append(current_group)
                current_group = [idx]
        groups.append(current_group)
        
        for g_idx, group in enumerate(groups):
            first_cue = transcript_items[group[0]]
            last_cue = transcript_items[group[-1]]
            
            # Context padding: expand slightly to catch introductory sentence
            raw_start = max(0.0, first_cue["start"] - 2.0)
            raw_end = last_cue["start"] + last_cue.get("duration", 3.0) + 2.0
            
            # Combine spoken text in segment
            full_segment_text = " ".join([transcript_items[i]["text"] for i in range(group[0], group[-1] + 1)])
            
            segments.append({
                "product_name": name,
                "variant": f"Take {g_idx + 1}" if len(groups) > 1 else "Primary Review",
                "raw_start": raw_start,
                "raw_end": raw_end,
                "snapped_start": raw_start, # Updated when audio snap is called
                "snapped_end": raw_end,
                "text_snippet": full_segment_text[:200] + ("..." if len(full_segment_text) > 200 else ""),
                "keywords_found": [k for k in keywords if k in full_segment_text.lower()]
            })
            
    return segments

def run_clip_pipeline(video_path: str, segments: list, upload_to_drive: bool = False, snap_audio: bool = True):
    """
    Runs micro-boundary snapping and cuts all approved segments.
    """
    results = []
    for seg in segments:
        raw_start = parse_time_str(seg["raw_start"])
        raw_end = parse_time_str(seg["raw_end"])
        
        start_ts = raw_start
        end_ts = raw_end
        
        if snap_audio and os.path.exists(video_path):
            # Scan only +- 2.5 seconds at the boundaries for natural speech pauses
            start_ts = snap_timestamp_to_silence(video_path, raw_start, search_radius=2.0, prefer_mode="nearest")
            end_ts = snap_timestamp_to_silence(video_path, raw_end, search_radius=2.0, prefer_mode="nearest")
            
        clean_name = re.sub(r'[^a-zA-Z0-9_]', '_', seg["product_name"].lower())
        out_filename = f"clip_{clean_name}_{int(start_ts)}s_{int(end_ts)}s.mp4"
        
        clip_path = None
        drive_status = "Not Requested"
        
        if os.path.exists(video_path):
            clip_path = slice_video(video_path, start_ts, end_ts, out_filename, lossless=True)
            if upload_to_drive:
                try:
                    drive_res = upload_clip_to_drive(clip_path)
                    drive_status = f"Uploaded ({drive_res})"
                except Exception as e:
                    drive_status = f"Error: {e}"
        
        results.append({
            "product_name": seg["product_name"],
            "start": format_time_code(start_ts),
            "end": format_time_code(end_ts),
            "duration": round(end_ts - start_ts, 2),
            "snapped": snap_audio,
            "local_clip_path": clip_path,
            "drive_status": drive_status
        })
        
    return results
