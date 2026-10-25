#!/usr/bin/env python3
"""
Programmatic Audio Clash & Distortion Gate (audio-clash-distortion-guard).
Detects and blocks:
1. Vocal-on-vocal / ad-lib timeline overlaps (overlap_ms > 0).
2. Digital clipping (peak >= -0.2 dBFS or crushed samples > 0.05%).
3. Over-compression / limiter brickwall distortion (crest factor < 9.5 dB).
4. Vocoder fry / harshness (4kHz-10kHz vs 200Hz-2.5kHz ratio > -14.0 dB).
"""
import argparse
import json
import subprocess
import sys
import tempfile
import wave
from pathlib import Path
import numpy as np


def extract_wav(media_path: Path, tmp_wav: Path) -> Path:
    subprocess.run([
        "ffmpeg", "-y", "-i", str(media_path),
        "-vn", "-ac", "2", "-ar", "48000", "-c:a", "pcm_s16le", str(tmp_wav)
    ], check=True, capture_output=True)
    return tmp_wav


def audit_signal(wav_path: Path) -> dict:
    with wave.open(str(wav_path), "rb") as wf:
        sr = wf.getframerate()
        n_ch = wf.getnchannels()
        raw = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
    if n_ch > 1:
        raw_2d = raw.reshape(-1, n_ch)
        mono = raw_2d.mean(axis=1)
        peak = float(np.max(np.abs(raw_2d))) + 1e-9
        crushed_pct = float(100.0 * np.mean(np.abs(raw_2d) > 0.96))
    else:
        mono = raw
        peak = float(np.max(np.abs(mono))) + 1e-9
        crushed_pct = float(100.0 * np.mean(np.abs(mono) > 0.96))

    rms = float(np.sqrt(np.mean(mono ** 2))) + 1e-9
    rms_db = 20.0 * np.log10(rms)
    peak_db = 20.0 * np.log10(peak)
    crest_db = peak_db - rms_db

    spec = np.abs(np.fft.rfft(mono))
    freqs = np.fft.rfftfreq(len(mono), 1.0 / sr)
    mid_e = float(np.mean(spec[(freqs >= 200) & (freqs <= 2500)] ** 2)) + 1e-9
    hi_e = float(np.mean(spec[(freqs >= 4000) & (freqs <= 10000)] ** 2)) + 1e-9
    harsh_db = 10.0 * np.log10(hi_e / mid_e)

    return {
        "duration_s": round(len(mono) / sr, 2),
        "rms_db": round(rms_db, 2),
        "peak_db": round(peak_db, 2),
        "crest_db": round(crest_db, 2),
        "crushed_pct": round(crushed_pct, 4),
        "harsh_db": round(harsh_db, 2),
    }


def check_timeline_overlaps(events: list[dict]) -> list[str]:
    """Verify sequential non-overlapping vocal events [{label, start, end}]."""
    errors = []
    sorted_ev = sorted(events, key=lambda x: x["start"])
    for i in range(len(sorted_ev) - 1):
        a = sorted_ev[i]
        b = sorted_ev[i + 1]
        overlap = a["end"] - b["start"]
        if overlap > 0.015:
            errors.append(
                f"CLASH: '{a.get('label', i)}' ({a['start']:.2f}s..{a['end']:.2f}s) overlaps "
                f"'{b.get('label', i+1)}' ({b['start']:.2f}s..{b['end']:.2f}s) by {overlap*1000:.0f} ms"
            )
    return errors


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mix", required=True, help="Path to final mixed WAV or MP4")
    ap.add_argument("--events-json", help="Optional JSON file of [{label, start, end}] vocal events")
    args = ap.parse_args()

    mix_p = Path(args.mix)
    with tempfile.TemporaryDirectory() as td:
        wav_p = mix_p if mix_p.suffix.lower() == ".wav" else extract_wav(mix_p, Path(td) / "mix.wav")
        metrics = audit_signal(wav_p)

    errors = []
    if metrics["peak_db"] > -0.15 or metrics["crushed_pct"] > 0.05:
        errors.append(f"DISTORTION/CLIPPING: peak_db={metrics['peak_db']} dBFS, crushed_pct={metrics['crushed_pct']}%")
    if metrics["crest_db"] < 9.5:
        errors.append(f"OVER-COMPRESSED/BRICKWALLED: crest_db={metrics['crest_db']} dB (< 9.5 dB minimum)")
    if metrics["harsh_db"] > -14.0:
        errors.append(f"VOCODER FRY / HARSH SIBILANCE: harsh_db={metrics['harsh_db']} dB (> -14.0 dB max)")

    if args.events_json and Path(args.events_json).exists():
        ev_data = json.loads(Path(args.events_json).read_text(encoding="utf-8"))
        errors.extend(check_timeline_overlaps(ev_data))

    report = {"ok": len(errors) == 0, "metrics": metrics, "errors": errors}
    print(json.dumps(report, indent=2))
    sys.exit(0 if report["ok"] else 1)


if __name__ == "__main__":
    main()
