# ⚡ DomAI Quickstart — MAVERICK™ 4K Video Director & Eden Mazara Commercial

Everything needed to edit, preview, and render the **Eden Mazara 4K Commercial (`3840×2160` UHD)** and the **4K Sizzle Reels** on **`DomAI`** is packaged for a single-command setup.

---

## 🚀 1. One-Command Bootstrap on `DomAI` (PowerShell)

Open PowerShell on **`DomAI`** and run:

```powershell
irm https://raw.githubusercontent.com/AIjennings/maverick-4k-video-director/main/setup-domai.ps1 | iex
```

### What This Command Does Automatically:
1. **Clones / Updates Repository:** Clones [`AIjennings/maverick-4k-video-director`](https://github.com/AIjennings/maverick-4k-video-director) (`dominic772` & `rykerrinehart82` invited with write access).
2. **Installs Agent Skills:** Installs `maverick-video-director` and `flow-cli` into Antigravity IDE (`~/.gemini/config/skills`), Hermes (`~/.hermes/skills`), and Claude Code (`~/.claude/skills`).
3. **Downloads Full 4K Project Workspace (`1.01 GB`):** Downloads and extracts `Eden-Mazara-4K-Project-Workspace.zip` (all 144 active keyframe-normalized 30fps video clips, 4K DJI stills, ElevenLabs v4 narration stems, music, HTML compositions, and EDL) into `eden-mazara-commercial/`.
4. **Installs HyperFrames & Launches Studio:** Runs `npm install` and launches `npx hyperframes preview` so the interactive timeline opens immediately on `DomAI`.

*(Optional: To also download the 3 pre-rendered 4K UHD MP4 masters into `renders/`, run `./setup-domai.ps1 -IncludeMasterRenders`.)*

---

## 🎬 2. Common Commands on `DomAI`

Inside the `eden-mazara-commercial` project directory:

- **Launch Interactive Studio Timeline:**
  ```powershell
  npx hyperframes preview
  ```
- **Run 10-Gate Broadcast & WCAG AA QA Audit:**
  ```powershell
  python ..\maverick-4k-video-director\qa\verify_commercial_v7.py
  ```
- **Re-Compile HTML Compositions from EDL (`build_v10_masterpiece.py`):**
  ```powershell
  python production\build_v10_masterpiece.py
  ```
- **Render Full 150s Commercial Master in Native 4K UHD (`3840×2160`):**
  ```powershell
  python production\normalize_keyframes_and_render_4k.py
  ```
- **Render 20s Website Sizzle & 45s LinkedIn Sizzle in Native 4K UHD (`3840×2160`):**
  ```powershell
  python production\rerender_derivatives_4k.py
  ```

---

## 📦 3. Shared Google Drive Vault (`3840×2160` 4K UHD Assets)

- **Master Shared Folder:** [MAVERICK 4K & Eden Mazara — Sizzle Reels & Launch Pack (4K UHD)](https://drive.google.com/drive/folders/1tlwUsgeHmwO2vzP-wl5i8wA88kOtnuhJ)
- **Full Editable HyperFrames Workspace (`1.01 GB` ZIP):** [`Eden-Mazara-4K-Project-Workspace.zip`](https://drive.google.com/file/d/1Rf5iakdFyCTnT-PR2mbHoFyH4B_GobnJ/view?usp=drivesdk)
- **20s Website Showcase Sizzle (`3840×2160`):** [`Eden-Mazara-4K-Website-Showcase-Sizzle-20s-3840x2160.mp4`](https://drive.google.com/file/d/1N3_NPqQS4Ll31fWP7Xjh6XhJGssXBkX9/view?usp=drivesdk)
- **45s LinkedIn Sizzle Reel (`3840×2160`):** [`MAVERICK-4K-LinkedIn-Sizzle-Reel-45s-3840x2160.mp4`](https://drive.google.com/file/d/1dzH22bgV4Jd5uipNJ70QPFpX8Kq3vPDL/view?usp=drivesdk)
- **150s Full Commercial Master (`3840×2160`):** [`Eden-Mazara-4K-Full-Commercial-Master-150s-3840x2160.mp4`](https://drive.google.com/file/d/1X3-w8n1nWvwkb1X-x3HxeLkmlsQAAIfx/view?usp=drivesdk)
