"""
End-to-End 10-Stage Runner & Verification Suite
Synthesizes a sample source video using FFmpeg, runs all 10 stages + Master Profile Manager,
and verifies outputs via Stage 10 QA (`ffprobe`).
"""

import os
import subprocess
from pathlib import Path
from engine import (
    load_master_profiles,
    get_active_profile,
    generate_packed_transcript_md,
    build_edl_storyboard,
    generate_overlay_specs,
    generate_top_layer_ass_subtitles,
    render_multi_aspect_and_concat,
    inspect_clip_qa,
    sync_catalog_database,
    BASE_DIR,
    MASTER_PROFILES_FILE
)

SAMPLE_VIDEO_ID = "nTp9hRWtlB4"
SAMPLE_SOURCE_MP4 = str(BASE_DIR / "cache" / "sample_source_review.mp4")

# Compressed timeline cues so we can test real FFmpeg slicing & QA rapidly on a 16-second test video
TEST_CUES = [
    {"start": 0.50, "duration": 1.80, "text": "Hey everyone! Today we're testing three ADHD timers."},
    {"start": 2.80, "duration": 2.20, "text": "First up is the flip cube timer rechargeable via USB-C."},
    {"start": 6.00, "duration": 2.50, "text": "Next let's look at the radial timer with the visual countdown disc."},
    {"start": 9.50, "duration": 2.80, "text": "And finally our third gadget is the timer capsule pill bottle."}
]

def create_synthetic_source_video(filepath: str):
    if os.path.exists(filepath):
        return filepath
    cmd = [
        "ffmpeg", "-y", "-hide_banner",
        "-f", "lavfi", "-i", "testsrc=duration=14:size=1280x720:rate=30",
        "-f", "lavfi", "-i", "sine=frequency=440:duration=14",
        "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k",
        filepath
    ]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    return filepath

def main():
    print("=================================================================")
    print("  ANTIGRAVITY CLIPSTUDIO: FULL 10-STAGE PIPELINE EXECUTION")
    print("=================================================================")

    # 0. Master Profile Manager
    master_store = load_master_profiles()
    active_prof = get_active_profile()
    print(f"[Master Profiles] Loaded {len(master_store['profiles'])} persistent presets from: {MASTER_PROFILES_FILE}")
    print(f"                  Active Preset: '{active_prof['name']}' (ID: {active_prof['id']})")

    # 1. Stage 1: Immutable Packed Transcript & Silence Map
    generate_packed_transcript_md(SAMPLE_VIDEO_ID, TEST_CUES)
    print(f"[Stage 1] Packed Transcript & Silence Map (`takes_packed.md`) generated.")

    # 2 & 3 & 4. Stage 2 (Cut Craft), Stage 3 (Brand Anchors), Stage 4 (EDL Storyboard)
    edl_doc = build_edl_storyboard(SAMPLE_VIDEO_ID, TEST_CUES, active_prof)
    print(f"[Stage 2-4] Plain-English EDL Storyboard built with {len(edl_doc['clips'])} product segments.")

    # 5. Stage 5: Programmatic Lower-Thirds & Callout Specs
    overlays = generate_overlay_specs(SAMPLE_VIDEO_ID, edl_doc, active_prof)
    print(f"[Stage 5] Generated {len(overlays)} cubic-bezier Lower-Third overlay specs (z-index: 20).")

    # 6. Stage 6: Top-Layer Dynamic Captions (ASS layer 30 - rendered LAST)
    for clip in edl_doc["clips"]:
        ass_file = generate_top_layer_ass_subtitles(SAMPLE_VIDEO_ID, clip, active_prof)
    print(f"[Stage 6] Generated Top-Layer `.ass` dynamic captions (z-index: 30, applied LAST).")

    # 7 & 8. Stage 7 (Multi-Aspect 16:9 + 9:16 Auto-Reframe) & Stage 8 (Concat Assembly)
    create_synthetic_source_video(SAMPLE_SOURCE_MP4)
    qa_reports = {}
    for clip in edl_doc["clips"]:
        rendered = render_multi_aspect_and_concat(SAMPLE_SOURCE_MP4, clip, active_prof)
        # 10. Stage 10: Automated QA (`ffprobe` 4-point check)
        qa_16_9 = inspect_clip_qa(rendered.get("16:9"), clip["duration"])
        qa_9_16 = inspect_clip_qa(rendered.get("9:16"), clip["duration"])
        qa_reports[clip["clip_id"]] = qa_16_9
        print(f"[Stage 7-8 & 10] Rendered & Verified '{clip['product_name']}':")
        print(f"                 • 16:9 Horizontal: {qa_16_9['resolution']} | {qa_16_9['actual_duration_sec']}s | {qa_16_9['overall_status']}")
        print(f"                 • 9:16 Vertical:   {qa_9_16['resolution']} | {qa_9_16['actual_duration_sec']}s | {qa_9_16['overall_status']}")

    # 9. Stage 9: Catalog Sync (CSV + JSON for Notion / Sheets / Drive)
    catalog_res = sync_catalog_database(SAMPLE_VIDEO_ID, edl_doc, qa_reports)
    print(f"[Stage 9] Synced {catalog_res['row_count']} verified clips to Catalog:")
    print(f"          CSV:  {catalog_res['csv_path']}")
    print(f"          JSON: {catalog_res['json_path']}")
    print("=================================================================")

if __name__ == "__main__":
    main()
