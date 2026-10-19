---
name: maverick-video-director
description: MAVERICK — Autonomous 4K Commercial & Investor Film Director ("Extreme Sports · Extreme Tech"). Use this skill whenever the user wants to create, direct, tune, verify, or render a broadcast-grade 4K commercial, investor film, motorsports sizzle, or luxury real estate showcase using the one-command Maverick pipeline (`maverick status|harvest|compile|verify|render-4k|ship`), Google Flow Spaceship CLI (`flow-cli`), ElevenLabs v4 narration, and deterministic HyperFrames A/B optical cross-dissolves.
metadata:
  version: "1.0.0"
  agent_name: "MAVERICK"
  brand: "Extreme Sports · Extreme Tech — Aria Technology Group"
---

# MAVERICK — Autonomous 4K Commercial & Investor Film Director

**MAVERICK** is Aria Technology Group's dedicated autonomous video production agent and deterministic 4K rendering engine, engineered around the **"Extreme Sports · Extreme Tech"** standard.

Instead of dragging clips by hand in timeline editors or accepting repetitive, low-resolution AI video slop, **MAVERICK** treats commercial filmmaking like deterministic systems engineering.

---

## One-Command Quickstart (`maverick`)

Run from anywhere using `./workspace\flow-cli\maverick.cmd` (or `python ./workspace\flow-cli\maverick.py`):

```powershell
# 1. Check WebBridge daemon, Google Flow session, Studio (:3003), and scratch disk
python ./workspace\flow-cli\maverick.py status

# 2. Harvest Veo 3.1 clips from Google Flow + enforce NTFS hardlink deduplication
python ./workspace\flow-cli\maverick.py harvest

# 3. Compile deterministic A/B dual-track optical cross-dissolve HTML compositions
python ./workspace\flow-cli\maverick.py compile

# 4. Run the 10-module automated QA & WCAG AA contrast verification suite
python ./workspace\flow-cli\maverick.py verify

# 5. Stream-render native 3840x2160 (4K UHD) 30fps master MP4
python ./workspace\flow-cli\maverick.py render-4k

# 6. Or run Compile -> Verify -> Render 4K end-to-end in ONE command:
python ./workspace\flow-cli\maverick.py ship
```

---

## The 5-Stage MAVERICK Architecture

### Stage 1: Hybrid Asset Harvesting & Hardlink Hygiene (`flow-cli`)
- **Spaceship Browser Bridge (`flow_cli.py`)**: Connects to the user's authenticated Google Flow Ultra session over Kimi WebBridge (`http://127.0.0.1:10086/command`).
- **In-Flow Custom Tools**: Automates `Beat Matched Cutter / Shot Explorer` (30 camera angles from an anchor frame), `GeoVisualizer` (3D satellite-to-drone orbits), and `Surface` (architectural material palettes).
- **Real Action + Generative Synthesis**: Blends authentic high-resolution regional action & DJI drone footage (e.g., real slow-motion golden-hour surfing at Witch's Rock *Roca Bruja* and 950-acre property aerials) with generative Veo 3.1 shots.
- **NTFS Hardlink Deduplication (`os.link`)**: Every asset is fingerprinted via SHA-256 and linked across project directories with zero duplicate multi-hundred-MB files on disk.

### Stage 2: ElevenLabs `eleven_v4` Narration & 24-Point Spectral Carve
- **Character-Aligned Voice Synthesis**: Generates expressive, conviction-driven narration per chapter (`ACT-01` through `ACT-05`) and extracts exact word/character timestamps into `CAPTION-CUES.json`.
- **24-Point Spectral Audio Ducking**: Automatically carves the music bed (`-9 dB` + mid-frequency EQ dip during spoken investor claims) and swells `+4 dB` into instrumental drops and golden-hour montages.

### Stage 3: Deterministic A/B Dual-Track Optical Compiler (`build_v10_masterpiece.py`)
- **Zero-Duplicate Invariant**: Enforces `135 cuts = 135 unique SHA-256 media files` (`max_usage_per_source = 1`) and `0` forbidden cartoon/CGI/watermarked assets.
- **Dual-Track A/B Optical Cross-Dissolves**: Alternates cuts between Track 1 (odd cuts) and Track 2 (even cuts) with `0.24s–0.36s` overlapping GSAP opacity cross-dissolves so there are zero jarring hard cuts.
- **Continuous Single-Tween Camera Glides**: Applies a single unbroken GSAP transform (`scale: 1.045 -> 1.0, ease: "sine.inOut", immediateRender: false`) across each video cut and continuous Ken Burns pans across every high-res photograph.

### Stage 4: 10-Module Opaque-Box Verification (`verify_commercial_v7.py`)
Validates 10 strict engineering gates before any 4K render begins:
1. `flow-cli` subcommand health (`status`, `tabs`, `tools`, `queue-status`, `index-assets`, `hygiene`)
2. Workspace NTFS hardlink hygiene (`0` unlinked duplicate MP4s `>10 KB`)
3. Master timeline continuity (`150.000s` exact, `0` gaps or overlaps `< 0.002s`)
4. Cut density & diversity (`>= 135` cuts, `100%` unique SHA-256 sources)
5. Forbidden asset exclusions (`0` out-of-region, annotated MLS, or fake CGI files)
6. `ffprobe` media duration bounds & internal dissolve avoidance
7. Seek-safe GSAP `fromTo` transforms (`immediateRender: false`) on 100% of static images
8. Transition ledger integrity (`134` optical transitions + camera handoffs)
9. `npx hyperframes check` (`0` errors, `100%` WCAG AA contrast across 28/28 text checks)
10. Live HyperFrames Studio preview server readiness (`http://localhost:3003`)

### Stage 5: High-Throughput 4K UHD Parallel Stream Render (`render-4k`)
- Routes Chromium/FFmpeg capture buffers to high-capacity scratch storage (`TEMP=./workspace\.hf-temp`) with `HF_CAPTURE_PARALLEL_STREAM=true` so 4,500+ native `3840x2160` frames pipe directly into H.264/NVENC without filling `C:`.
