#!/usr/bin/env python3
"""
Beat-Drop 808 Spectral Scanner (audio-clash-distortion-guard).
Scans any instrumental MP3/WAV/MP4 in 0.5-second windows for:
- Overall RMS energy (dBFS)
- 35-120 Hz 808 / sub-bass energy
Automatically identifies the exact timestamp where the full 808 + Drum Drop hits
(e.g., 26.15s-51.80s in Walk It Talk It W6iBTxdR-DI rather than the quiet intro).
"""
import argparse
import json
import subprocess
import tempfile
import wave
from pathlib import Path
import numpy as np


def main():
    ap = argparse.ArgumentParser(description="Find the exact 808/Drum Beat-Drop window in an instrumental")
    ap.add_argument("--audio", required=True, help="Path to instrumental MP3/WAV/MP4")
    ap.add_argument("--max-sec", type=float, default=90.0, help="Max duration to scan (seconds)")
    args = ap.parse_args()

    src = Path(args.audio)
    with tempfile.TemporaryDirectory() as td:
        tmp_wav = Path(td) / "scan.wav"
        subprocess.run([
            "ffmpeg", "-y", "-i", str(src), "-t", str(args.max_sec),
            "-vn", "-ac", "1", "-ar", "48000", str(tmp_wav)
        ], check=True, capture_output=True)
        with wave.open(str(tmp_wav), "rb") as wf:
            sr = wf.getframerate()
            s = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0

    step = int(0.5 * sr)
    windows = []
    for i in range(0, len(s) - step, step):
        seg = s[i:i + step]
        rms_db = 20.0 * np.log10(float(np.sqrt(np.mean(seg ** 2))) + 1e-9)
        peak_db = 20.0 * np.log10(float(np.max(np.abs(seg))) + 1e-9)
        spec = np.abs(np.fft.rfft(seg))
        freqs = np.fft.rfftfreq(len(seg), 1.0 / sr)
        bass_energy = float(np.mean(spec[(freqs >= 35) & (freqs <= 120)]))
        windows.append({
            "t_start": round(i / sr, 2),
            "t_end": round((i + step) / sr, 2),
            "rms_db": round(rms_db, 2),
            "peak_db": round(peak_db, 2),
            "bass_35_120hz": round(bass_energy, 1),
        })

    max_bass = max((w["bass_35_120hz"] for w in windows), default=1.0)
    drop_windows = [w for w in windows if w["bass_35_120hz"] >= 0.45 * max_bass and w["rms_db"] >= -15.5]
    first_drop_s = drop_windows[0]["t_start"] if drop_windows else 0.0
    pickup_start_s = max(0.0, round(first_drop_s - 1.35, 2))

    summary = {
        "audio": str(src),
        "first_full_808_drop_s": first_drop_s,
        "recommended_pickup_slice_start_s": pickup_start_s,
        "top_drop_windows": drop_windows[:20],
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
