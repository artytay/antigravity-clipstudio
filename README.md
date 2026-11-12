# Antigravity ClipStudio

Automated AI Video Clipping Studio with Parent-Child Lineage, Fast-GOP Proxy Engine, and Google Drive / YouTube Sync.

Designed for high-throughput video creators to auto-segment, auto-transcribe, and generate multi-aspect ratio clips (16:9 widescreen reviews, 9:16 high-retention viral shorts, and clean B-roll demo assets) with millisecond Cut-Craft boundary accuracy.

---

## 🚀 Live Web App & Mobile Access

- **Live GitHub Pages App:** [https://artytay.github.io/antigravity-clipstudio/](https://artytay.github.io/antigravity-clipstudio/)
- **Optimized for:** iPhone Safari (mobile touch controls, responsive fluid columns) and Mac desktop.

---

## ⚡ Key Capabilities

1. **Interactive Project Wizard (`What do you want to do?` & `To what video?`):**
   - Goal-based AI segmenter (Product Reviews, Viral Hooks, Clean B-Roll).
   - Source selector connected to live YouTube uploads (`UCBncVyCemJoHiIK7ge6keFw`), Google Drive folders (`Source Videos [Clipstudio]`), and Google Takeout archives.
2. **7-Stage Drive Readiness Matrix:**
   - Real-time diagnostic tracker showing: Drive Folder Hierarchy, Master Video File in Drive, Raw Transcript Loaded, Detailed `takes_packed.md` with silence map, Audio Profiling, Lineage Mapping, and Uploaded Clips.
3. **Parent-Child Clip Lineage & Deduplication Graph:**
   - Tracks 3-tier hierarchy: Level 0 Master -> Level 1 Parent Clip -> Level 2 Child Subclip.
   - Prevents duplicate clip renders while linking subclips back to both their parent clip and the original master video.
4. **Fast-GOP 360p Video Proxy Engine & 2GB LRU Disk Budget:**
   - Automatically generates lightweight 360p H.264 proxies with 15-frame keyframe intervals for zero-buffering scrubbing on mobile.
   - Dynamic 6fps animated preview GIFs for instant hover-scrubbing.
   - Strict 2GB (2,048 MB) LRU cache budget with automatic eviction.
5. **Google Drive Non-Media Settings Grid:**
   - Visual file-type badges (JSON configuration, Markdown notes, CSV spreadsheets, Drive folders) with direct links to Google Drive.
6. **Google Gemini Direct Drive Scanner:**
   - One-click auto-discovery of newly uploaded raw video files across Google Drive folders.

---

## 📂 Google Drive Hierarchy

- **Root Video Editor Folder:** [`ANTIGRAVITY | Video Editor`](https://drive.google.com/drive/folders/1wF355bFfBSyiS_N1tMkONQWWozuNjIQ0) (`1wF355bFfBSyiS_N1tMkONQWWozuNjIQ0`)
  - **Source Videos Folder:** [`Source Videos [Clipstudio]`](https://drive.google.com/drive/folders/1PLLjdQtqU9JxdVWsbXJZ5N5z6lSpNqwW) (`1PLLjdQtqU9JxdVWsbXJZ5N5z6lSpNqwW`)
    - **Full Videos:** `Full Videos/` (`1Fg1MkNaxC5m7Fqzi_-RSZled2ymxkCvk`)
      - `<Video Title>/`: e.g. `3 Epic ADHD Timers` (`1kX2lDJC6I306sqT79QbBmINNcSP_7rQN`)
        - `3 EPIC ADHD TIMERS...mp4` (87.0 MB Master File: `1gGjzFKXmDSS_dR0aCzlF84M4TvZTIvl8`)
        - `takes_packed.md` (Silence Map & Immutable Packed Transcript)
        - `clip_lineage_tree.json` (Deduplication Graph)
        - `Clips/`: (`1dzQaejxrM3Y6Gqe58BazhdsEq5PdMPai`)
  - **ClipStudio Settings & Takeouts:** [`Clipstudio`](https://drive.google.com/drive/folders/17N2FTWKILTfObOIkrJTfAslILQyzFs9e) (`17N2FTWKILTfObOIkrJTfAslILQyzFs9e`)
    - `Clipstudio Settings/` (`1cghO_UEYcRGBDmuLIbeE7xcaXBebBEBd`)
      - `master_profiles.json`
      - `source_videos_registry.json`
      - `takeout_registry.json`
      - `clip_lineage_catalog.csv`
      - `CLIPSTUDIO_CHANGELOG.md`

---

## 🛠 Local Development & Backend Server

```bash
# Clone the repository
git clone https://github.com/artytay/antigravity-clipstudio.git
cd antigravity-clipstudio

# Run the live video playback & REST server
python3 server.py --port 8085
```

Open `http://localhost:8085` in your browser.
