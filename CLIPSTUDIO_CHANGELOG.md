# Antigravity ClipStudio — Architecture & Change Notes
**Last Synced:** `2026-11-12 04:46:10 UTC`
**Clipstudio Drive Folder ID:** `17N2FTWKILTfObOIkrJTfAslILQyzFs9e`
**Clipstudio Settings Folder ID:** `1cghO_UEYcRGBDmuLIbeE7xcaXBebBEBd`
**Main Video Editor Folder ID:** `1wF355bFfBSyiS_N1tMkONQWWozuNjIQ0`
**Connected YouTube Channel:** `UCBncVyCemJoHiIK7ge6keFw`

---

## Version History & Capabilities

### v5.0 — Google Takeout Unpacker & Cloud Settings Sync
- **Cloud Settings Sync:** Automatically backs up `master_profiles.json`, `takeout_registry.json`, and `CLIPSTUDIO_CHANGELOG.md` directly into your `Clipstudio` and `Clipstudio Settings` Google Drive folders.
- **Google Takeout Automated Scanner & Unpacker (`takeout_manager.py`):**
  - Scans your Google Drive for `takeout-*.zip` archives and `Takeout*` folders (discovered 12 Takeout zip archives and 10 Takeout folders).
  - Unpacks `.mp4`, `.mov`, `.mkv`, and `.webm` videos, deduplicates against your existing `ANTIGRAVITY | Video Editor` library, uploads only missing videos, and registers them as clippable sources inside ClipStudio.
  - Includes a one-click **Request YouTube Takeout to Drive** launcher pre-configured for `dest=DRIVE`.

### v4.0 — Floating PiP Follower, Auto-Scroll & Embedded Drive/Channel Viewers
- **Floating Picture-in-Picture (PiP) Reframe Mirror:** Follows scroll across all tabs, mirroring 16:9 / 9:16 crop, timecode, Z-20 Lower-Thirds, and Z-30 Top-Layer Captions.
- **Auto-Scroll on Preview:** Smoothly scrolls back to the Main Monitor with a focus pulse whenever `Preview` is clicked.
- **Embedded Google Drive & YouTube Channel Viewers:** Dedicated tabs for browsing your Drive folder and scrubbing your YouTube channel (`UCBncVyCemJoHiIK7ge6keFw`).

### v1.0 – v3.5 — Complete 10-Stage Creator Automation Pipeline
1. **Stage 1 (`takes_packed.md`):** Immutable phrase-level transcript cache with millisecond silence safety badges (`>=400ms CLEAN`, `150-399ms PHRASE`, `<150ms UNSAFE`).
2. **Stage 2 (Cut Craft):** `-50ms` pre-word padding, `+80ms` post-word padding, `25ms` anti-pop `afade`, and `+-2.0s` local silence snapping.
3. **Stage 3 (Brand & Product Anchors):** Persistent keyword & affiliate link mappings.
4. **Stage 4 (EDL Storyboard):** Plain-English Edit Decision List (`nTp9hRWtlB4_edl_plan.json`).
5. **Stage 5 (Z-20 Lower-Thirds):** Cubic-bezier (`0.22, 1, 0.36, 1`) product callout cards.
6. **Stage 6 (Z-30 Top-Layer Captions):** `.ass` dynamic word-pill subtitles rendered LAST above all overlays.
7. **Stage 7 (Dual Aspect Auto-Reframe):** Simultaneous `16:9` horizontal and `9:16` vertical Shorts export.
8. **Stage 8 (Concat Assembly):** Zero-reencode FFmpeg concat manifests for Intro + Review + Outro slates.
9. **Stage 9 (Drive & Notion Catalog):** Automated CSV & JSON asset catalog (`clip_asset_library.csv`).
10. **Stage 10 (`ffprobe` 4-Point QA):** Automated verification of video stream, audio stream, resolution, and duration (`PASSED_4_OF_4_CHECKS`).
