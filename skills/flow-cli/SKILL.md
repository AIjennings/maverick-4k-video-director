---
name: flow-cli
description: Drive Google Flow in the user's real browser via Kimi WebBridge daemon (127.0.0.1:10086) for zero-click multi-shot commercial generation, Veo 3.1 - Lite batch queuing, custom tool automation (Surface, GeoVisualizer, Shot Explorer), asset harvesting with NTFS hardlink deduplication, and asset indexing.
metadata:
  version: "1.0.0"
---

# Google Flow "Spaceship" CLI (`flow-cli`) Companion Skill

The `flow-cli` tool automates the user's authenticated Google Flow (`flow.google.com`) browser session via the local Kimi WebBridge daemon (`http://127.0.0.1:10086`). It provides programmatic control for video generation, side-panel AI agent batch queuing, custom in-Flow tool execution, media harvesting, and NTFS hardlink deduplication.

## Prerequisites

1. **WebBridge Daemon**: Active and listening at `http://127.0.0.1:10086/command` (default address).
2. **Authenticated Google Flow Tab**: User logged into `flow.google.com` (Project: `00000000-0000-0000-0000-flowproject01`, Ultra tier).
3. **Environment**: Python 3.10+ and `ffprobe` / `ffmpeg` available on PATH.

## Command Reference

Run using `python ./workspace\flow-cli\flow_cli.py <subcommand> [flags]` or `flow-cli <subcommand> [flags]`.

All commands output structured JSON (`{"ok": true, "data": ...}` or `{"ok": false, "error": ...}`) and exit `0` on success.

### 1. `flow-cli status`
Probes WebBridge daemon, browser session, user auth, ULTRA tier, project ID, and reCAPTCHA status.
```bash
python ./workspace\flow-cli\flow_cli.py status
```
Returns:
```json
{
  "ok": true,
  "data": {
    "daemon_running": true,
    "daemon_url": "http://127.0.0.1:10086",
    "authenticated": true,
    "user": "director@yourdomain.com",
    "tier": "ULTRA",
    "project_id": "00000000-0000-0000-0000-flowproject01",
    "project_title": "Eden Mazara — Regional Experience Pickups",
    "active_tab_id": 334592805,
    "recaptcha_warning": false,
    "ready_for_generation": true
  }
}
```

### 2. `flow-cli tabs`
Discovers open browser tabs matching Google Flow and classifies their roles (`project`, `clip_editor`, `tool_editor`, `tool_community`).
```bash
python ./workspace\flow-cli\flow_cli.py tabs
```

### 3. `flow-cli tools`
Inspects custom tools pinned in the Flow project:
- **`Beat Matched Cutter` / `Remix of Shot Explorer`** (`00000000-0000-0000-0000-shotexplorer`): Generates 30 visually consistent, location-locked camera angles (overhead, side, back, pan, tilt, zoom) from an anchor image via `🍌 Nano Banana 2.1`.
- **`Surface`** (`community-00000000-0000-0000-0000-surfacetool1`): Defines tropical materials (teak, volcanic stone, lime plaster, infinity water) to design luxury villa & sanctuary scenes.
- **`Remix of GeoVisualizer`** (`00000000-0000-0000-0000-geovisualizr`): Visualizes 3D coastal geography and satellite-to-drone orbit visualization using pigeon-maps and Omni 1.1 Flash.
- **`Text Effect`**: Kinetic typography treatments.

Flags:
- `--inspect <tool-id-or-name>`: Query details and active state of a specific tool.

### 4. `flow-cli queue-status`
Audits the side-panel AI agent thread and project media grid tiles, reporting completed, in-progress, and failed generations.
```bash
python ./workspace\flow-cli\flow_cli.py queue-status
```

### 5. `flow-cli submit-batch`
Submits multi-shot batch prompts to the in-browser Flow AI Agent using `Veo 3.1 - Lite [Lower Priority]` (16:9 landscape, 0 credits).
Features automatic reCAPTCHA preflight: detects idle connection warnings and triggers tab reload before submission.
```bash
python ./workspace\flow-cli\flow_cli.py submit-batch [--prompt "<text>" | --file <path>]
```

### 6. `flow-cli harvest`
Discovers signed Google Cloud CDN video URLs (`https://flow-content.google/video/<uuid>?...`), downloads full-resolution 720p 24fps MP4s, computes SHA-256 hashes, deduplicates against existing workspace files via NTFS hardlinks (`os.link`), and updates `manifest.json`.
```bash
python ./workspace\flow-cli\flow_cli.py harvest [--output-dir <path>]
```

### 7. `flow-cli index-assets`
Runs `ffprobe` and `ffmpeg` frame-decode checks across all harvested MP4s, verifying duration, resolution, fps, and codec integrity. Generates or updates `NEW-PICKUPS-CATALOG.json`.
```bash
python ./workspace\flow-cli\flow_cli.py index-assets [--dir <path>]
```

### 8. `flow-cli hygiene`
Recursively audits workspace (`./workspace`) for duplicate MP4 files (>10 KB). Replaces unlinked duplicate files with NTFS hardlinks (`os.link`) sharing identical inodes (`st_ino`), guaranteeing 0 duplicate multi-hundred-MB files.
```bash
python ./workspace\flow-cli\flow_cli.py hygiene [--root-dir <path>] [--dry-run]
```

## Guardrails & Operational Constraints

1. **Never Close User Tabs**: Always attach tabs using `borrowed: true`. Never invoke `close_tab` or `close_session` on user tabs.
2. **Zero-Credit Model Enforcement**: Strictly select `Veo 3.1 - Lite [Lower Priority]` (unlimited free credits). Never interact with paid credit upgrade modals.
3. **Transport Protocol**: Always communicate with WebBridge using Python standard library `urllib.request` over HTTP POST JSON to avoid Windows shell quoting and encoding corruption.
4. **NTFS Hardlink Invariant**: All duplicate MP4 copies (>10KB) across `eden-mazara*` must share filesystem inodes via `os.link`.
