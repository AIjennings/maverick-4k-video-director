<!-- Standard ARIA WIRE™ Open Source Repository Header -->

<p align="center">
  <a href="https://www.ariawave.tech">
    <img src="https://www.ariawave.tech/AriaLogoWhiteLarge.png" alt="ARIA Logo" width="180" />
  </a>
</p>

<p align="center">
  <a href="https://www.ariawave.tech/wire-map?utm_source=github&utm_medium=repo-badge&utm_campaign=maverick-4k"><img src="https://img.shields.io/badge/ARIA_WIRE%E2%84%A2-Wire_Your_Company-0ea5e9?style=for-the-badge" alt="ARIA WIRE" /></a>
  <a href="https://www.ariawave.tech/case-studies/eden-mazara-4k-commercial"><img src="https://img.shields.io/badge/MAVERICK-4K_Autonomous_Director-10b981?style=for-the-badge" alt="MAVERICK 4K" /></a>
  <a href="https://youtu.be/JfgRN4uejUM"><img src="https://img.shields.io/badge/YouTube-Watch_4K_Proof-ef4444?style=for-the-badge" alt="Watch 4K Proof" /></a>
</p>

# MAVERICK™ — Autonomous 4K Commercial & Investor Film Director

> **Part of the ARIA WIRE™ Open Source Suite • "Extreme Sports · Extreme Tech"**  
> Deterministic HTML-to-4K video compilation, hybrid drone/action + generative Veo 3.1 harvesting (`flow-cli`), ElevenLabs `eleven_v4` character-aligned narration, 24-point spectral audio ducking, and 10-module automated WCAG AA verification.

---

## Why We Built MAVERICK

Most AI video workflows today fail for high-stakes commercial and capital-raising work:
- **Timeline Slop:** Prompting a model for random 4-second clips leaves you with jarring hard cuts, repeated shots, hallucinations, and dead audio gaps.
- **$150K Agency Bottlenecks:** Traditional luxury real estate, motorsports, and capital-markets films take 8–12 weeks and six-figure production crews.

**MAVERICK** treats commercial filmmaking like **deterministic systems engineering**. Given real drone/action telemetry, generative Google Flow pickups, a musical beat grid, and an investor thesis, Maverick compiles a seek-safe HTML5/GSAP master composition and stream-renders native **3840×2160 (4K UHD)** broadcast masters with **zero duplicate cuts** and **100% automated QA verification**.

### Live Production Proof: *Eden Mazara — 950-Acre Costa Rica Investor & Lifestyle Film (2:30, 4K UHD)*
- 🎬 **Watch the 4K Master on YouTube:** [https://youtu.be/JfgRN4uejUM](https://youtu.be/JfgRN4uejUM)
- 📖 **Read the Engineering Case Study:** [ariawave.tech/case-studies/eden-mazara-4k-commercial](https://www.ariawave.tech/case-studies/eden-mazara-4k-commercial)
- 📊 **Verified Production Telemetry:**
  - **Duration:** `150.000s` exact across 5 chapters (`place`, `basis`, `lots`, `water`, `close`)
  - **Picture Cuts:** `135` beat-locked cuts across `135` unique SHA-256 media files (`0` duplicate cuts)
  - **Optical Transitions:** `134` A/B dual-track optical cross-dissolves (`0.24s–0.36s` overlap) + continuous single-tween camera glides
  - **Audio Architecture:** ElevenLabs `eleven_v4` character-aligned voiceover + 24-point spectral EQ/gain ducking envelope
  - **Automated QA:** `10/10` opaque-box verification modules passed (`28/28` WCAG AA contrast checks, `0` timeline gaps `< 0.002s`)

---

## Architecture: The 5-Stage Autonomous Pipeline

```
┌────────────────────────────────────────────────────────────────────────────┐
│ STAGE 1: HYBRID HARVEST & NTFS HARDLINK HYGIENE (cli/flow_cli.py)          │
│ • Drives Google Flow (Veo 3.1 - Lite) + Custom Tools (Shot Explorer /      │
│   Beat Matched Cutter, GeoVisualizer, Surface) over Kimi WebBridge         │
│ • Blends authentic 4K DJI drone aerials & slow-motion action (Witch's Rock │
│   golden-hour surf) with generative pickups                                │
│ • SHA-256 fingerprinting + NTFS hardlink deduplication (os.link)           │
└──────────────────────────────────────┬─────────────────────────────────────┘
                                       ▼
┌────────────────────────────────────────────────────────────────────────────┐
│ STAGE 2: VOICE SYNTHESIS & 24-POINT SPECTRAL CARVE                         │
│ • ElevenLabs eleven_v4 expressive narration with character-level timing    │
│ • 24-point automated gain & mid-frequency EQ carve (-9 dB under voice,     │
│   +4 dB swell on musical drops and golden-hour montages)                   │
└──────────────────────────────────────┬─────────────────────────────────────┘
                                       ▼
┌────────────────────────────────────────────────────────────────────────────┐
│ STAGE 3: DETERMINISTIC A/B OPTICAL COMPILER (compiler/build_v10_*.py)      │
│ • Alternates cuts across Track 1 (odd) & Track 2 (even) with 0.24s–0.36s   │
│   overlapping GSAP opacity cross-dissolves                                 │
│ • Single unbroken GSAP camera glide (scale 1.045 → 1.0) per cut            │
│ • WCAG AA executive telemetry cards (#142c25 emerald + #d9be84 gold)       │
└──────────────────────────────────────┬─────────────────────────────────────┘
                                       ▼
┌────────────────────────────────────────────────────────────────────────────┐
│ STAGE 4: 10-MODULE OPAQUE-BOX QA SUITE (qa/verify_commercial_v7.py)        │
│ • Verifies CLI contract, hardlink hygiene, 150.000s timeline continuity,   │
│   0 duplicate SHA-256 hashes, ffprobe duration bounds, GSAP seek-safety,   │
│   and npx hyperframes check (28/28 WCAG AA contrast checks)                │
└──────────────────────────────────────┬─────────────────────────────────────┘
                                       ▼
┌────────────────────────────────────────────────────────────────────────────┐
│ STAGE 5: PARALLEL 4K UHD STREAM RENDER (cli/maverick.py render-4k)         │
│ • Streams 4,500 native 3840x2160 frames with HF_CAPTURE_PARALLEL_STREAM    │
│   and high-capacity scratch routing into H.264 / NVENC 4K MP4              │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ One-Command Quickstart (`maverick`)

```bash
# 1. Inspect pipeline readiness (WebBridge daemon, Google Flow tab, Studio :3003, scratch disk)
python cli/maverick.py status

# 2. Harvest completed Veo 3.1 clips from Google Flow & enforce NTFS hardlink deduplication
python cli/maverick.py harvest

# 3. Compile deterministic A/B dual-track optical cross-dissolve HTML compositions
python cli/maverick.py compile

# 4. Run the 10-module opaque-box QA & WCAG AA verification suite
python cli/maverick.py verify

# 5. Stream-render native 3840x2160 (4K UHD) 30fps master MP4
python cli/maverick.py render-4k

# 6. Or run Compile → Verify → Render 4K end-to-end in a single command:
python cli/maverick.py ship
```

---

## 📦 Repository Contents

| Path | Description |
| :--- | :--- |
| `cli/maverick.py` | Single-command autonomous film director CLI (`status`, `harvest`, `compile`, `verify`, `render-4k`, `ship`) |
| `cli/flow_cli.py` | Google Flow "Spaceship" CLI driving `flow.google.com` & custom tools (`Shot Explorer`, `GeoVisualizer`, `Surface`) via WebBridge (`127.0.0.1:10086`) |
| `compiler/build_v10_masterpiece.py` | Deterministic A/B dual-track optical cross-dissolve & beat-locked HTML5/GSAP composition compiler |
| `compiler/build_v7_compositions.py` | Core Ken Burns camera motion & executive WCAG AA telemetry card primitives |
| `qa/verify_commercial_v7.py` | 10-module opaque-box verification suite (`ffprobe` bounds, SHA-256 uniqueness, WCAG AA contrast, timeline math) |
| `skills/maverick-video-director/SKILL.md` | Agent skill definition for Claude Code, Codex, Hermes, and Google Antigravity |
| `skills/flow-cli/SKILL.md` | Companion skill for browser-bridged Google Flow automation & NTFS hardlink hygiene |
| `skills/audio-clash-distortion-guard/SKILL.md` | Pre-delivery audio QA gate (`verify_audio_mix.py`), 808 Beat-Drop spectral scanner (`scan_beat_drop.py`), Lip-Sync-Locked ElevenLabs Speech-to-Speech (`eleven_multilingual_sts_v2`), and 5-stage Studio Vocal-to-Beat Glue Chain |

---

## 🏢 Turnkey Autonomous 4K Film Production & Enterprise Deployment

Want **Aria Technology Group** to direct and deliver a broadcast-grade 4K investor film, motorsports sizzle, or product launch commercial — or deploy the **MAVERICK** pipeline inside your own marketing and capital-raising team?

- 🎬 **Case Study & Service Packages:** [ariawave.tech/case-studies/eden-mazara-4k-commercial](https://www.ariawave.tech/case-studies/eden-mazara-4k-commercial)
- 🗺️ **Build Your Company's Wire Map:** [ariawave.tech/wire-map](https://www.ariawave.tech/wire-map?utm_source=github&utm_medium=repo-readme&utm_campaign=maverick-4k-video-director)
- 📞 **Book an Executive Strategy Session:** [ariawave.tech/#contact](https://www.ariawave.tech/#contact)

---

<p align="center">
  Licensed under the MIT License • Engineered by <a href="https://www.ariawave.tech">Aria Technology Group</a> ("Extreme Sports · Extreme Tech")
</p>
