import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time

PROJECT_DIR = Path(r"./workspace\eden-mazara-commercial")
TEMP_DIR = Path(r"./workspace\.hf-temp")
TEMP_DIR.mkdir(parents=True, exist_ok=True)


def run_full_4k_render() -> None:
  print("Compiling V10 compositions...", flush=True)
  subprocess.run(
      [
          sys.executable,
          str(PROJECT_DIR / "production" / "build_v10_masterpiece.py"),
      ],
      cwd=str(PROJECT_DIR),
      check=True,
  )

  out_tmp = PROJECT_DIR / "eden-mazara-commercial-v10-4k-fresh.mp4"
  out_final = PROJECT_DIR / "eden-mazara-commercial-v10-4k.mp4"
  out_downloads = Path(r"~\Downloads\eden-mazara-commercial-v10-4k.mp4")

  env = os.environ.copy()
  env["TEMP"] = str(TEMP_DIR)
  env["TMP"] = str(TEMP_DIR)
  env["HF_CAPTURE_PARALLEL_STREAM"] = "true"

  npx_bin = shutil.which("npx.cmd") or shutil.which("npx") or "npx"
  cmd = [
      npx_bin,
      "hyperframes",
      "render",
      "--output",
      str(out_tmp),
      "--resolution",
      "landscape-4k",
      "--fps",
      "30",
      "--quality",
      "high",
      "--frames-cache-dir",
      str(TEMP_DIR / "hf-extract-cache"),
  ]
  print(
      "Starting full 3840x2160 4K UHD HyperFrames render (--resolution"
      " landscape-4k)...",
      flush=True,
  )
  t0 = time.time()
  subprocess.run(cmd, cwd=str(PROJECT_DIR), env=env, check=True)
  elapsed = time.time() - t0
  print(f"Full 4K render finished in {elapsed:.1f}s!", flush=True)

  if out_tmp.is_file() and out_tmp.stat().st_size > 50_000_000:
    if out_final.exists():
      out_final.unlink()
    out_tmp.rename(out_final)
    if out_downloads.exists():
      out_downloads.unlink()
    try:
      os.link(out_final, out_downloads)
    except OSError:
      shutil.copy2(out_final, out_downloads)
    print(f"Updated 4K master at {out_final} and {out_downloads}", flush=True)

    # Refresh 4K showcase and 4K LinkedIn sizzle from the newly rendered 4K master
    subprocess.run(
        [
            sys.executable,
            str(PROJECT_DIR / "production" / "rerender_derivatives_4k.py"),
        ],
        cwd=str(PROJECT_DIR),
        check=True,
    )


if __name__ == "__main__":
  run_full_4k_render()
