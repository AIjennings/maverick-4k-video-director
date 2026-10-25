---
name: audio-clash-distortion-guard
description: Mandatory pre-delivery audio QA gate and mix architecture skill for AI music videos, rap remixes, voiceovers, and lip-sync shorts. Detects and blocks vocal-on-vocal clashes, ad-lib collisions, double-track beat/song phase clashes, digital clipping/distortion, aggressive time-stretch warble, and audio-to-lip desync before any video is shipped to Telegram or the user.
---

# Audio Clash & Distortion Guard (`audio-clash-distortion-guard`)

Use this skill **before** rendering or shipping any multi-voice, music-backed, or lip-synced video. It provides both the **Mix Architecture Rules** (how to synthesize and mix vocals + beats without clashes or distortion) and the **Programmatic Pre-Flight Gate (`scripts/verify_audio_mix.py`)** that must pass (`exit code 0`) before delivery.

---

## Why AI Music & Vocal Mixes Fail (The 5 Fatal Sins to Never Repeat)

1. **Fatal Sin #1 — Vocal-on-Vocal & Ad-Lib Collisions (`overlap > 0 ms`)**
   - **What goes wrong:** Placing separate ad-lib clips (`"SKRRT!"`, `"COMPUTE!"`, `"SEND THE INVOICE!"`) at hardcoded timestamps (`start=2.55s`) while the lead vocal bar is still speaking (`0.10s..3.40s`), or overlapping consecutive bars (`bar1` ends at `4.6s`, `bar2` starts at `3.7s`). The human ear hears two voices talking over each other as chaotic, unintelligible noise.
   - **The Rule:** **Sequential non-overlapping timeline placement only.** Every vocal event `i` must start at `t_start[i] >= t_end[i-1] + 0.06s` (minimum `60ms` breath pocket), OR ad-libs must be spoken naturally inline as part of the bar. Never layer 3 separate TTS generations of the same sentence as "unison" (they have different syllable durations and create a 3-voice trainwreck).

2. **Fatal Sin #2 — Double-Music / Original-Song Vocal Clash**
   - **What goes wrong:** Mixing the original song (with the original artist's vocals and drums) AND a separate instrumental track at the same time underneath AI vocals. Two unaligned drum tracks cause severe comb-filtering/phase cancellation, and the original artist's vocals clash directly with the AI vocals.
   - **The Rule:** **Single clean instrumental bed only during verses.** Never layer two music files simultaneously. If using an intro hook from the original song, hard-crossfade (`acrossfade`) from the intro hook into the clean instrumental *before* the first AI vocal word begins.

3. **Fatal Sin #3 — Gain-Staging & DSP Distortion (`0.0 dBFS` Brickwall Crushing)**
   - **What goes wrong:** Setting ElevenLabs `stability=0.0` + `style=0.96` (which causes neural vocoder fry and screaming artifacts), then applying `treble=g=4.5` + `acompressor=makeup=2.2` + `loudnorm=-12` on each clip, and then multiplying by `volume=1.35` into `amix(normalize=0)`. The summed signal hits `+8 dBFS` and slams into the brickwall limiter, producing harsh, nasty distortion.
   - **The Rule:**
     - **ElevenLabs Voice Settings:** Keep `stability` between **`0.32` and `0.50`** and `style` between **`0.35` and `0.65`** (`eleven_multilingual_v2` or `eleven_english_sts_v2`). Never use `stability=0.0` with `style > 0.85`.
     - **No Bracket-Tag Prompts in TTS Text:** Never pass `[excited, swaggering Atlanta trap flow]` or `[shouting hyped]` inside the text string — TTS models either read the bracket words out loud or glitch on them. Drive cadence via **Speech-to-Speech (`/v1/speech-to-speech/{voice_id}`)** or natural punctuation (`!`, `...`, `—`).
     - **No Extreme `atempo` Warble:** Never exceed `atempo=1.15` (above `1.15x`, FFmpeg's WSOLA time-stretcher introduces metallic phase warble). Write tighter lyrics instead of speeding up audio by `1.25x–1.42x`.
     - **Clean Gain Staging:** Do NOT apply `treble` boosts or heavy `acompressor` makeup on individual TTS clips. Normalize the final vocal bus once (`loudnorm=I=-14:TP=-1.5:LRA=9`) and mix the instrumental bed at `-19 LUFS` (`volume=0.32–0.38`) with clean headroom (`True Peak <= -1.0 dBFS`).

4. **Fatal Sin #4 — Replacing Audio on Pre-Rendered Lip-Sync Video**
   - **What goes wrong:** Generating a lip-sync video (`OmniHuman` / `Kling`) from Stem A, then swapping in a newly synthesized Stem B during `ffmpeg` muxing. The mouth movements no longer match the words.
   - **The Rule:** Every lip-sync video clip must use the **exact audio stream** it was generated from — OR upgrade the stem via **ElevenLabs Speech-to-Speech (`/v1/speech-to-speech/{voice_id}`)** which preserves the exact syllable timing and mouth sync of the original stem while upgrading vocal emotion and timbre.

5. **Fatal Sin #5 — Slicing the Wrong Part of the Instrumental (`0:00` Intro Trap)**
   - **What goes wrong:** Slicing `0:00–0:50` of a YouTube instrumental assuming the beat drops immediately. Most rap/trap instrumentals (e.g. *Walk It Talk It* `https://youtu.be/W6iBTxdR-DI`) have a `13s–26s` ambient pad or quiet flute intro before the iconic `808 + Drum Drop` hits at `26.15s`.
   - **The Rule:** Always run `scripts/scan_beat_drop.py` on the instrumental first to locate the exact timestamp where `35–120 Hz` 808 energy and RMS peak (`first_full_808_drop_s`), then slice `1.35s` before the drop (`recommended_pickup_slice_start_s`) so a brief melodic pickup leads straight into the full drum knock on Verse 1.

---

## Proven Studio Workflows & Methods

### Method 1: Beat-Drop 808 Spectral Scanner (`scripts/scan_beat_drop.py`)
Never guess where the beat drops in a reference instrumental. Run:

```bash
python "C:/Users/Aria/.gemini/config/skills/audio-clash-distortion-guard/scripts/scan_beat_drop.py" \
  --audio "path/to/instrumental.mp3"
```

- Scans `0.5s` windows for `35–120 Hz` 808 sub-bass energy and RMS level.
- Outputs `first_full_808_drop_s` (e.g. `26.15s` in `W6iBTxdR-DI`) and `recommended_pickup_slice_start_s` (`24.80s`).
- If the active drop section (`26.15s–51.80s`) is shorter than the full video (`45.32s`), loop the active drop section seamlessly with a `120ms` `acrossfade` (`d=0.12:c1=tri:c2=tri`) so the 808 knock never drops out mid-rap.

### Method 2: Lip-Sync-Locked ElevenLabs Speech-to-Speech Emotion Upgrade
When you already have lip-synced video clips (`OmniHuman` / `Kling`) whose timing is locked to existing vocal stems, **do not regenerate from text** (which changes syllable durations and breaks mouth sync). Instead, feed each lip-synced stem into ElevenLabs Speech-to-Speech (`/v1/speech-to-speech/{voice_id}`):

```python
# Endpoint: POST https://api.elevenlabs.io/v1/speech-to-speech/{voice_id}?output_format=mp3_44100_192
data = {
    "model_id": "eleven_multilingual_sts_v2",
    "voice_settings": json.dumps({
        "stability": 0.38,
        "similarity_boost": 0.92,
        "style": 0.62,
        "use_speaker_boost": True,
    }),
}
```
- **Why this works:** Speech-to-Speech transfers the expressive voice clone and style onto the exact prosody and syllable timestamps of the input stem — `0 ms` lip-sync drift and `0` bracket-tag TTS glitches.

### Method 3: Studio Vocal-to-Beat Glue Chain (Solving "Vocal & Beat Sound Separate")
When AI vocals sit on top of a beat like a dry podcast voiceover instead of feeling inside the record, apply this **5-stage FFmpeg Studio Glue Filtergraph**:

1. **Stronger Beat Presence + 808 Sub-Bass Warmth (`volume=0.78`):**
   - Bring the instrumental up to `volume=0.78` (around `-14.5 LUFS` integrated mix) with `+2.2 dB` at `62 Hz` (`equalizer=f=62:t=q:w=1.1:g=2.2`) so the 808 knock and flute hook carry real weight.
2. **Complementary `2.4 kHz`Vocal Pocket Carve:**
   - Carve `-1.8 dB` at `2400 Hz` (`equalizer=f=2400:t=q:w=1.2:g=-1.8`) in the instrumental bed right where vocal consonant clarity lives, and trim `-1.5 dB` at `240 Hz` (`equalizer=f=240:t=q:w=1.4:g=-1.5`) on the vocal stem to remove dry TTS boxiness.
3. **Subtle Studio Trap Room Slap / Stereo Doubler (Music Section Only):**
   - Split the vocal bus (`asplit=2[vo_music_in][vo_dry_in]`). During the music section (`0..cut_s`), add a subtle `28ms | 56ms` stereo studio slap and `1.16x` width (`aecho=0.85:0.88:28|56:0.12|0.07,extrastereo=m=1.16`). After the record-scratch silence cut (`t >= cut_s`), switch to `vo_dry` so dead-silence comedic lines stay bone-dry and close-mic'd.
4. **Gentle `1.85:1` Sidechain Pocket Ducking:**
   - Use `sidechaincompress=threshold=0.055:ratio=1.85:attack=18:release=165:makeup=1.08` so the beat breathes `~1.5 dB` around every bar without pumping or disappearing.
5. **Shared `2.0:1` SSL-Style Master Bus Glue Compressor:**
   - Sum `[ducked_music][vo_glued]` through `amix=inputs=2:duration=longest:normalize=0`, then compress them **together** through `acompressor=threshold=-14dB:ratio=2.0:attack=25:release=140:makeup=1.12` followed by `loudnorm=I=-13.2:TP=-1.2:LRA=8.5`. Because the 808s and vocals move the same master VCA envelope together, the vocal locks directly into the beat.

---

## Mandatory Pre-Delivery Verification CLI

Run `verify_audio_mix.py` on the vocal timeline manifest + final mixed WAV/MP4 before delivering any video:

```bash
python "C:/Users/Aria/.gemini/config/skills/audio-clash-distortion-guard/scripts/verify_audio_mix.py" \
  --mix "path/to/final_master.mp4" \
  --events-json "path/to/timeline_events.json"
```

### What `verify_audio_mix.py` Enforces (`exit 0` required):
1. **Zero Timeline Overlap Gate:** Verifies that no two vocal clips in `--events-json` overlap (`overlap_ms <= 15 ms`).
2. **Clipping & Crest Factor Gate:** Rejects any mix with `peak > -0.15 dBFS`, `crushed_pct > 0.05%`, or `crest_db < 9.5 dB` (over-compressed/brickwalled distortion).
3. **High-Frequency Harshness / Vocoder Fry Gate:** Measures the `4 kHz – 10 kHz` to `200 Hz – 2.5 kHz` spectral energy ratio and rejects mixes where sibilance/fry exceeds `-14.0 dB`.
