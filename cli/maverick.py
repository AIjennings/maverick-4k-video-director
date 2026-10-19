#!/usr/bin/env python3
"""
MAVERICK — Autonomous 4K Commercial & Investor Film Director CLI
"Extreme Sports · Extreme Tech" | ARIA WIRE™ Open Source Suite

One-command orchestrator for the 5-stage Autonomous 4K Video Production Pipeline:
  1. maverick status     — Check WebBridge daemon, Google Flow session, Studio (:3003), and temp disk space
  2. maverick harvest    — Harvest Veo 3.1 clips from Google Flow + enforce NTFS hardlink deduplication
  3. maverick compile    — Compile beat-locked A/B dual-track optical cross-dissolve HTML compositions
  4. maverick verify     — Run the 10-module automated QA & WCAG AA contrast verification suite
  5. maverick render-4k  — Stream-render deterministic 3840x2160 (4K UHD) 30fps master MP4
  6. maverick ship       — Run compile -> verify -> render-4k end-to-end in a single command
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from typing import Any

WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
FLOW_CLI_PATH = Path(__file__).resolve().parent / "flow_cli.py"
DEFAULT_PROJECT_DIR = WORKSPACE_ROOT / "eden-mazara-commercial"
DEFAULT_TEMP_DIR = WORKSPACE_ROOT / ".hf-temp"


def run_step(cmd: list[str], cwd: Path, env: dict[str, str] | None = None) -> tuple[int, str, str]:
    proc = subprocess.run(
        cmd,
        cwd=str(cwd),
        env=env or os.environ.copy(),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return proc.returncode, proc.stdout, proc.stderr


def cmd_status(args: argparse.Namespace) -> dict[str, Any]:
    project_dir = Path(args.project_dir).resolve()
    DEFAULT_TEMP_DIR.mkdir(parents=True, exist_ok=True)
    disk_usage = shutil.disk_usage(str(DEFAULT_TEMP_DIR))
    free_gb = round(disk_usage.free / (1024 ** 3), 2)

    # Check Studio server on :3003
    studio_alive = False
    try:
        req = urllib.request.Request("http://127.0.0.1:3003", method="GET")
        with urllib.request.urlopen(req, timeout=3) as resp:
            studio_alive = resp.status == 200
    except Exception:
        studio_alive = False

    # Check flow-cli status
    rc, out, _ = run_step([sys.executable, str(FLOW_CLI_PATH), "status"], cwd=WORKSPACE_ROOT)
    flow_status = {}
    try:
        flow_status = json.loads(out).get("data", {})
    except Exception:
        flow_status = {"raw": out.strip(), "exit_code": rc}

    edl_path = project_dir / "production" / "EDIT-DECISION-LIST.json"
    edl_summary = {}
    if edl_path.is_file():
        try:
            edl_data = json.loads(edl_path.read_text(encoding="utf-8"))
            if isinstance(edl_data, list) and edl_data:
                last_cut = edl_data[-1]
                edl_summary = {
                    "version": "V10.0",
                    "total_duration": round(float(last_cut.get("start", 0)) + float(last_cut.get("duration", 0)), 3),
                    "total_cuts": len(edl_data),
                    "unique_sources": len({c.get("source") for c in edl_data}),
                    "optical_cross_dissolves": max(0, len(edl_data) - 1),
                }
            elif isinstance(edl_data, dict):
                edl_summary = {
                    "version": edl_data.get("version"),
                    "total_duration": edl_data.get("total_duration"),
                    "total_cuts": edl_data.get("summary", {}).get("total_cuts"),
                    "unique_sources": edl_data.get("summary", {}).get("unique_sources"),
                    "optical_cross_dissolves": edl_data.get("summary", {}).get("optical_cross_dissolves"),
                }
        except Exception:
            pass

    return {
        "ok": True,
        "agent": "MAVERICK — Autonomous 4K Film Director",
        "brand": "Extreme Sports · Extreme Tech (ARIA WIRE™)",
        "data": {
            "project_dir": str(project_dir),
            "temp_dir": str(DEFAULT_TEMP_DIR),
            "free_disk_gb": free_gb,
            "studio_server_port_3003": studio_alive,
            "flow_bridge": flow_status,
            "active_edl": edl_summary,
        },
    }


def cmd_harvest(args: argparse.Namespace) -> dict[str, Any]:
    rc1, out1, err1 = run_step([sys.executable, str(FLOW_CLI_PATH), "harvest"], cwd=WORKSPACE_ROOT)
    rc2, out2, err2 = run_step([sys.executable, str(FLOW_CLI_PATH), "hygiene"], cwd=WORKSPACE_ROOT)
    rc3, out3, err3 = run_step([sys.executable, str(FLOW_CLI_PATH), "index-assets"], cwd=WORKSPACE_ROOT)
    return {
        "ok": rc1 == 0 and rc2 == 0 and rc3 == 0,
        "agent": "MAVERICK",
        "step": "harvest",
        "data": {
            "harvest_rc": rc1,
            "hygiene_rc": rc2,
            "index_rc": rc3,
        },
    }


def cmd_compile(args: argparse.Namespace) -> dict[str, Any]:
    project_dir = Path(args.project_dir).resolve()
    compiler = project_dir / "production" / "build_v10_masterpiece.py"
    if not compiler.is_file():
        return {"ok": False, "error": f"Compiler script not found at {compiler}"}
    t0 = time.time()
    rc, out, err = run_step([sys.executable, str(compiler)], cwd=project_dir)
    return {
        "ok": rc == 0,
        "agent": "MAVERICK",
        "step": "compile",
        "duration_sec": round(time.time() - t0, 2),
        "output": out.strip(),
        "stderr": err.strip() if rc != 0 else "",
    }


def cmd_verify(args: argparse.Namespace) -> dict[str, Any]:
    project_dir = Path(args.project_dir).resolve()
    verifier = project_dir / "production" / "verify_commercial_v7.py"
    if not verifier.is_file():
        return {"ok": False, "error": f"Verifier script not found at {verifier}"}
    cmd = [sys.executable, str(verifier), "--json"]
    if args.fast:
        cmd.append("--fast")
    if args.skip_snapshots:
        cmd.append("--skip-snapshots")
    rc, out, err = run_step(cmd, cwd=project_dir)
    try:
        report = json.loads(out)
    except Exception:
        report = {"raw_stdout": out.strip(), "raw_stderr": err.strip()}
    return {
        "ok": rc == 0,
        "agent": "MAVERICK",
        "step": "verify",
        "report": report,
    }


def cmd_render_4k(args: argparse.Namespace) -> dict[str, Any]:
    project_dir = Path(args.project_dir).resolve()
    DEFAULT_TEMP_DIR.mkdir(parents=True, exist_ok=True)
    output_file = Path(args.output).resolve() if args.output else (project_dir / "eden-mazara-commercial-v10-4k.mp4")

    env = os.environ.copy()
    env["TEMP"] = str(DEFAULT_TEMP_DIR)
    env["TMP"] = str(DEFAULT_TEMP_DIR)
    env["HF_CAPTURE_PARALLEL_STREAM"] = "true"

    npx_bin = shutil.which("npx.cmd") or shutil.which("npx") or "npx"
    cmd = [
        npx_bin,
        "hyperframes",
        "render",
        "--output",
        str(output_file),
        "--width",
        str(args.width),
        "--height",
        str(args.height),
        "--fps",
        str(args.fps),
        "--quality",
        args.quality,
    ]
    t0 = time.time()
    rc, out, err = run_step(cmd, cwd=project_dir, env=env)
    size_mb = round(output_file.stat().st_size / (1024 ** 2), 2) if output_file.is_file() else 0.0
    return {
        "ok": rc == 0 and output_file.is_file() and size_mb > 10.0,
        "agent": "MAVERICK",
        "step": "render-4k",
        "duration_sec": round(time.time() - t0, 2),
        "output_file": str(output_file),
        "size_mb": size_mb,
        "resolution": f"{args.width}x{args.height}",
        "fps": args.fps,
        "stdout_tail": out.strip()[-600:],
        "stderr_tail": err.strip()[-600:] if rc != 0 else "",
    }


def cmd_ship(args: argparse.Namespace) -> dict[str, Any]:
    compile_res = cmd_compile(args)
    if not compile_res.get("ok"):
        return {"ok": False, "failed_stage": "compile", "details": compile_res}

    args.fast = False
    args.skip_snapshots = True
    verify_res = cmd_verify(args)
    if not verify_res.get("ok"):
        return {"ok": False, "failed_stage": "verify", "details": verify_res}

    render_res = cmd_render_4k(args)
    return {
        "ok": bool(render_res.get("ok")),
        "agent": "MAVERICK",
        "step": "ship",
        "compile": compile_res,
        "verify_passed": verify_res.get("ok"),
        "render": render_res,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="maverick",
        description="MAVERICK — Autonomous 4K Commercial & Investor Film Director ('Extreme Sports · Extreme Tech')",
    )
    parser.add_argument(
        "--project-dir",
        default=str(DEFAULT_PROJECT_DIR),
        help="Path to the HyperFrames commercial project directory",
    )

    sub = parser.add_subparsers(dest="subcommand", required=True)

    sub.add_parser("status", help="Inspect WebBridge, Google Flow, Studio server (:3003), and disk health")
    sub.add_parser("harvest", help="Harvest completed Veo 3.1 clips, deduplicate via NTFS hardlinks, and index")
    sub.add_parser("compile", help="Compile deterministic A/B dual-track optical transitions & HTML compositions")

    p_verify = sub.add_parser("verify", help="Run the 10-module opaque-box QA & WCAG AA verification suite")
    p_verify.add_argument("--fast", action="store_true", help="Skip headless browser checks for fast iteration")
    p_verify.add_argument("--skip-snapshots", action="store_true", default=True, help="Skip snapshot re-capture")

    p_render = sub.add_parser("render-4k", help="Stream-render native 3840x2160 4K UHD master MP4")
    p_render.add_argument("--output", default="", help="Output MP4 path")
    p_render.add_argument("--width", type=int, default=3840, help="Render width (default: 3840)")
    p_render.add_argument("--height", type=int, default=2160, help="Render height (default: 2160)")
    p_render.add_argument("--fps", type=int, default=30, help="Frame rate (default: 30)")
    p_render.add_argument("--quality", default="high", choices=["draft", "standard", "high"], help="Render quality")

    p_ship = sub.add_parser("ship", help="Compile -> Verify -> Render 4K end-to-end in one command")
    p_ship.add_argument("--output", default="", help="Output MP4 path")
    p_ship.add_argument("--width", type=int, default=3840)
    p_ship.add_argument("--height", type=int, default=2160)
    p_ship.add_argument("--fps", type=int, default=30)
    p_ship.add_argument("--quality", default="high")

    args = parser.parse_args()
    dispatch = {
        "status": cmd_status,
        "harvest": cmd_harvest,
        "compile": cmd_compile,
        "verify": cmd_verify,
        "render-4k": cmd_render_4k,
        "ship": cmd_ship,
    }
    res = dispatch[args.subcommand](args)
    print(json.dumps(res, indent=2))
    return 0 if res.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
