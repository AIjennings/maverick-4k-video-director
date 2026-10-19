#!/usr/bin/env python3
"""Automated Opaque-Box Verification Test Suite for Eden Mazara 2:30 Commercial (V7).

This test suite executes 10 independent verification modules evaluating:
  1. CLI Subcommands Contract (`flow-cli` status, tabs, tools, queue-status, index-assets, hygiene)
  2. Workspace Hardlink Data Hygiene (0 unlinked duplicate MP4s >10KB across eden-mazara*)
  3. Master Timeline Duration & Gaps (exact 150.000s, 5 chapters, <0.002s tolerance)
  4. Cut Count & Source Diversity (>=135 cuts, >=75 sources, 0 back-to-back dupes, max repeat <=2)
  5. Forbidden Asset Exclusions (0 out-of-region clips, 0 raw MLS survey-annotated photos)
  6. FFprobe Media Bounds & Internal Dissolve Windows (media duration bounds, dissolve avoidance)
  7. Seek-Safe GSAP Transforms (100% <img> cuts have fromTo with immediateRender: false)
  8. Transition Ledger Integrity (>=75 verified transitions bound to active cut boundaries)
  9. HyperFrames Standards & WCAG AA Contrast (`npx hyperframes check` 0 errors, 100% contrast)
  10. Live Studio Preview Server Health (port 3003 HTTP 200 OK, non-disruptive)

Usage:
  python production/verify_commercial_v7.py [OPTIONS]

Options:
  --fast, --skip-browser   Skip headless browser validation and snapshots for fast iteration
  --skip-snapshots         Run hyperframes check but skip snapshot generation
  --snapshots              Force capture and verification of visual snapshots
  --skip-cli               Skip flow-cli verification (focus on commercial composition only)
  --module <id|name>       Run only a specific module (1-10 or name fragment)
  --json                   Output structured JSON envelope on stdout
  --verbose, -v            Enable detailed diagnostic logging
  --help, -h               Show this help message and exit

Exit Code:
  0: All executed verification modules passed
  1: One or more verification assertions failed
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
COMMERCIAL_ROOT = SCRIPT_DIR.parent
WORKSPACE_ROOT = COMMERCIAL_ROOT.parent

# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------

@dataclass
class AssertionFailure:
    module_id: int
    module_name: str
    assertion: str
    details: str
    remediation: str | None = None

@dataclass
class ModuleResult:
    module_id: int
    name: str
    passed: bool
    duration_sec: float
    message: str
    details: dict[str, Any] = field(default_factory=dict)
    failures: list[AssertionFailure] = field(default_factory=list)

@dataclass
class VerificationSuiteReport:
    timestamp: str
    all_passed: bool
    total_modules: int
    passed_modules: int
    failed_modules: int
    duration_sec: float
    modules: list[ModuleResult] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Module 1: CLI Subcommands Health (`flow-cli`)
# ---------------------------------------------------------------------------

def check_cli_subcommands(verbose: bool = False) -> ModuleResult:
    """Verifies flow-cli subcommands exit 0 with structured JSON envelopes."""
    t0 = time.time()
    module_id = 1
    name = "cli_subcommands"
    failures: list[AssertionFailure] = []
    details: dict[str, Any] = {}

    # Locate flow-cli executable
    flow_cli_py = WORKSPACE_ROOT / "flow-cli" / "flow_cli.py"
    flow_cli_cmd = WORKSPACE_ROOT / "flow-cli" / "flow-cli.cmd"
    cli_runner: list[str] | None = None

    if flow_cli_py.is_file():
        cli_runner = [sys.executable, str(flow_cli_py)]
    elif flow_cli_cmd.is_file():
        cli_runner = [str(flow_cli_cmd)]
    else:
        which_cli = shutil.which("flow-cli")
        if which_cli:
            cli_runner = [which_cli]

    if not cli_runner:
        failures.append(AssertionFailure(
            module_id=module_id,
            module_name=name,
            assertion="flow-cli executable exists",
            details=f"Could not locate flow-cli at {flow_cli_py} or on PATH",
            remediation="Implement flow-cli in ./workspace\\flow-cli\\flow_cli.py per R1 spec."
        ))
        return ModuleResult(
            module_id=module_id,
            name=name,
            passed=False,
            duration_sec=time.time() - t0,
            message="flow-cli executable not found",
            details=details,
            failures=failures,
        )

    details["cli_runner"] = cli_runner

    # 1. Test --help
    try:
        proc_help = subprocess.run(
            [*cli_runner, "--help"],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=str(WORKSPACE_ROOT),
        )
        if proc_help.returncode != 0:
            failures.append(AssertionFailure(
                module_id=module_id,
                module_name=name,
                assertion="flow-cli --help exits 0",
                details=f"Exit code: {proc_help.returncode}, stderr: {proc_help.stderr.strip()}",
                remediation="Fix argument parser in flow_cli.py to handle --help cleanly.",
            ))
        else:
            details["help_output_len"] = len(proc_help.stdout)
    except Exception as exc:
        failures.append(AssertionFailure(
            module_id=module_id,
            module_name=name,
            assertion="flow-cli --help executes without exception",
            details=str(exc),
        ))

    # 2. Test core subcommands
    subcommands = ["status", "tabs", "tools", "queue-status", "index-assets", "hygiene"]
    details["subcommand_results"] = {}

    for subcmd in subcommands:
        extra_args: list[str] = []
        if subcmd == "hygiene":
            extra_args = ["--dry-run"]
        elif subcmd == "index-assets":
            extra_args = ["--dir", str(COMMERCIAL_ROOT / "assets" / "flow")]

        cmd = [*cli_runner, subcmd, *extra_args]
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=15,
                cwd=str(WORKSPACE_ROOT),
            )
            stdout = proc.stdout.strip()
            stderr = proc.stderr.strip()

            if proc.returncode != 0:
                failures.append(AssertionFailure(
                    module_id=module_id,
                    module_name=name,
                    assertion=f"flow-cli {subcmd} exits 0",
                    details=f"Exit code: {proc.returncode}, stdout: {stdout[:200]}, stderr: {stderr[:200]}",
                    remediation=f"Ensure `flow-cli {subcmd}` handles environment state and exits 0.",
                ))
                details["subcommand_results"][subcmd] = {"returncode": proc.returncode, "error": stderr[:200]}
                continue

            # Verify structured JSON
            try:
                data = json.loads(stdout)
                if not isinstance(data, dict):
                    raise ValueError("Output must be a JSON object")
                if not data.get("ok"):
                    failures.append(AssertionFailure(
                        module_id=module_id,
                        module_name=name,
                        assertion=f"flow-cli {subcmd} returns ok: true",
                        details=f"JSON response did not indicate success: {stdout[:200]}",
                    ))
                details["subcommand_results"][subcmd] = {"ok": True, "keys": list(data.keys())}
            except Exception as json_err:
                failures.append(AssertionFailure(
                    module_id=module_id,
                    module_name=name,
                    assertion=f"flow-cli {subcmd} outputs valid JSON envelope",
                    details=f"Parse error: {json_err}, stdout snippet: {stdout[:200]}",
                    remediation=f"Ensure `flow-cli {subcmd}` emits valid JSON `{{\"ok\": true, ...}}`.",
                ))
                details["subcommand_results"][subcmd] = {"json_error": str(json_err)}

        except subprocess.TimeoutExpired:
            failures.append(AssertionFailure(
                module_id=module_id,
                module_name=name,
                assertion=f"flow-cli {subcmd} completes within 15s",
                details="Command timed out",
                remediation=f"Check if {subcmd} is waiting on an unresponsive network/daemon socket.",
            ))
        except Exception as exc:
            failures.append(AssertionFailure(
                module_id=module_id,
                module_name=name,
                assertion=f"flow-cli {subcmd} executes without exception",
                details=str(exc),
            ))

    passed = len(failures) == 0
    return ModuleResult(
        module_id=module_id,
        name=name,
        passed=passed,
        duration_sec=time.time() - t0,
        message="All CLI subcommands verified" if passed else f"{len(failures)} CLI subcommand check(s) failed",
        details=details,
        failures=failures,
    )


# ---------------------------------------------------------------------------
# Module 2: Workspace Hardlink Hygiene (`eden-mazara*`)
# ---------------------------------------------------------------------------

def check_workspace_hardlink_hygiene(verbose: bool = False) -> ModuleResult:
    """Verifies 0 unlinked duplicate MP4s (>10KB) across eden-mazara* via NTFS inode identity."""
    t0 = time.time()
    module_id = 2
    name = "workspace_hardlink_hygiene"
    failures: list[AssertionFailure] = []
    details: dict[str, Any] = {}

    # Discover target project roots matching eden-mazara*
    target_dirs: list[Path] = [
        p for p in WORKSPACE_ROOT.iterdir()
        if p.is_dir() and p.name.startswith("eden-mazara")
    ]
    details["scanned_directories"] = [str(d) for d in target_dirs]

    mp4_files: list[Path] = []
    ignored_parts = {".git", ".agents", "node_modules", "__pycache__", ".hyperframes", "dist"}

    for tdir in target_dirs:
        for root, dirs, files in os.walk(tdir):
            dirs[:] = [d for d in dirs if d not in ignored_parts]
            for f in files:
                if f.lower().endswith(".mp4"):
                    full_p = Path(root) / f
                    try:
                        st = full_p.stat()
                        # Requirement: files > 10KB (10240 bytes)
                        if st.st_size > 10240:
                            mp4_files.append(full_p)
                    except OSError:
                        pass

    details["total_mp4_files_scanned"] = len(mp4_files)

    # Compute SHA-256 and collect inodes
    hash_to_files: dict[str, list[tuple[Path, int, int]]] = {}
    for p in mp4_files:
        try:
            h = hashlib.sha256()
            with open(p, "rb") as f:
                while chunk := f.read(65536):
                    h.update(chunk)
            digest = h.hexdigest()
            st = p.stat()
            hash_to_files.setdefault(digest, []).append((p, st.st_ino, st.st_nlink))
        except Exception as exc:
            failures.append(AssertionFailure(
                module_id=module_id,
                module_name=name,
                assertion=f"Read and hash MP4 file {p.name}",
                details=str(exc),
            ))

    duplicate_groups = {k: v for k, v in hash_to_files.items() if len(v) > 1}
    details["duplicate_hash_groups"] = len(duplicate_groups)

    unlinked_duplicates = 0
    unlinked_details: list[dict[str, Any]] = []

    for digest, file_list in duplicate_groups.items():
        inodes = {st_ino for _, st_ino, _ in file_list}
        if len(inodes) > 1:
            unlinked_duplicates += (len(file_list) - 1)
            unlinked_details.append({
                "hash": digest[:12],
                "files": [str(p) for p, _, _ in file_list],
                "inodes": list(inodes),
            })

    details["unlinked_duplicates_count"] = unlinked_duplicates
    details["unlinked_details"] = unlinked_details[:10]  # truncate for brevity

    if unlinked_duplicates > 0:
        failures.append(AssertionFailure(
            module_id=module_id,
            module_name=name,
            assertion="0 unlinked duplicate MP4 copies (>10KB) across eden-mazara*",
            details=f"Found {unlinked_duplicates} unlinked duplicate MP4 copies across {len(unlinked_details)} hash groups.",
            remediation="Run `flow-cli hygiene` or link duplicates via `os.link` to preserve disk hygiene.",
        ))

    passed = len(failures) == 0
    return ModuleResult(
        module_id=module_id,
        name=name,
        passed=passed,
        duration_sec=time.time() - t0,
        message="Hardlink data hygiene 100% compliant" if passed else f"{unlinked_duplicates} unlinked duplicate MP4s found",
        details=details,
        failures=failures,
    )


# ---------------------------------------------------------------------------
# Module 3: Timeline Duration & Gap Math
# ---------------------------------------------------------------------------

def check_timeline_duration_and_gaps(verbose: bool = False) -> ModuleResult:
    """Asserts exact 150.000s duration across the 5 chapters with 0 gaps or overlaps (<0.002s)."""
    t0 = time.time()
    module_id = 3
    name = "timeline_duration_and_gaps"
    failures: list[AssertionFailure] = []
    details: dict[str, Any] = {}

    # Prefer EDL-V7-PROPOSAL.json if present, else EDIT-DECISION-LIST.json
    edl_path = COMMERCIAL_ROOT / "production" / "EDL-V7-PROPOSAL.json"
    if not edl_path.is_file():
        edl_path = COMMERCIAL_ROOT / "production" / "EDIT-DECISION-LIST.json"

    if not edl_path.is_file():
        failures.append(AssertionFailure(
            module_id=module_id,
            module_name=name,
            assertion="Active EDL JSON file exists",
            details=f"Neither EDL-V7-PROPOSAL.json nor EDIT-DECISION-LIST.json found in {COMMERCIAL_ROOT / 'production'}",
        ))
        return ModuleResult(
            module_id=module_id,
            name=name,
            passed=False,
            duration_sec=time.time() - t0,
            message="EDL not found",
            details=details,
            failures=failures,
        )

    details["edl_path"] = str(edl_path)
    with open(edl_path, "r", encoding="utf-8") as f:
        edl_data = json.load(f)

    # Expected chapter specs per R2 / Acceptance Criteria
    expected_chapters = {
        "place": {"start": 0.0, "duration": 30.0, "end": 30.0},
        "basis": {"start": 30.0, "duration": 30.0, "end": 60.0},
        "lots": {"start": 60.0, "duration": 35.0, "end": 95.0},
        "water": {"start": 95.0, "duration": 30.0, "end": 125.0},
        "close": {"start": 125.0, "duration": 25.0, "end": 150.0},
    }

    # Verify total film duration
    if not edl_data:
        failures.append(AssertionFailure(
            module_id=module_id,
            module_name=name,
            assertion="EDL is not empty",
            details="EDL contains 0 cuts",
        ))
        return ModuleResult(module_id=module_id, name=name, passed=False, duration_sec=time.time() - t0, message="Empty EDL", failures=failures)

    total_first_start = float(edl_data[0]["start"])
    last_cut = edl_data[-1]
    total_last_end = float(last_cut["start"]) + float(last_cut["duration"])
    total_duration = total_last_end - total_first_start

    details["total_duration"] = round(total_duration, 4)
    if abs(total_duration - 150.0) >= 0.002:
        failures.append(AssertionFailure(
            module_id=module_id,
            module_name=name,
            assertion="Total duration equals 150.000s (<0.002s tolerance)",
            details=f"Calculated total duration is {total_duration:.4f}s (expected 150.000s)",
            remediation="Adjust chapter cut durations to sum to exactly 150.000s.",
        ))

    # Verify per-chapter continuity, gaps, and overlaps
    by_chapter: dict[str, list[dict[str, Any]]] = {}
    for cut in edl_data:
        chap = cut.get("chapter", "unknown")
        by_chapter.setdefault(chap, []).append(cut)

    details["chapters_found"] = list(by_chapter.keys())

    for chap_name, spec in expected_chapters.items():
        cuts = by_chapter.get(chap_name, [])
        if not cuts:
            failures.append(AssertionFailure(
                module_id=module_id,
                module_name=name,
                assertion=f"Chapter '{chap_name}' cuts present in EDL",
                details=f"Chapter '{chap_name}' has 0 cuts in EDL",
            ))
            continue

        cuts_sorted = sorted(cuts, key=lambda c: float(c["start"]))
        chap_start = float(cuts_sorted[0]["start"])
        chap_last = cuts_sorted[-1]
        chap_end = float(chap_last["start"]) + float(chap_last["duration"])
        chap_dur = chap_end - chap_start

        if abs(chap_start - spec["start"]) >= 0.002:
            failures.append(AssertionFailure(
                module_id=module_id,
                module_name=name,
                assertion=f"Chapter '{chap_name}' start matches spec ({spec['start']}s)",
                details=f"Chapter '{chap_name}' starts at {chap_start:.4f}s",
            ))

        if abs(chap_dur - spec["duration"]) >= 0.002:
            failures.append(AssertionFailure(
                module_id=module_id,
                module_name=name,
                assertion=f"Chapter '{chap_name}' duration matches spec ({spec['duration']}s)",
                details=f"Chapter '{chap_name}' duration is {chap_dur:.4f}s (expected {spec['duration']}s)",
            ))

        # Check internal cut gaps and overlaps
        for i in range(len(cuts_sorted) - 1):
            curr_c = cuts_sorted[i]
            next_c = cuts_sorted[i + 1]
            curr_end = float(curr_c["start"]) + float(curr_c["duration"])
            next_start = float(next_c["start"])
            delta = next_start - curr_end

            if abs(delta) >= 0.002:
                gap_type = "gap" if delta > 0 else "overlap"
                failures.append(AssertionFailure(
                    module_id=module_id,
                    module_name=name,
                    assertion=f"Chapter '{chap_name}' has 0 {gap_type}s (<0.002s)",
                    details=f"Cut {i} (id={curr_c.get('id')}) to cut {i+1} has {gap_type} of {abs(delta):.4f}s at t={curr_end:.3f}s",
                    remediation=f"Recalibrate cut durations in chapter '{chap_name}' to eliminate {gap_type}.",
                ))

    # Also inspect HTML composition files on disk
    html_dir = COMMERCIAL_ROOT / "compositions"
    details["html_files_checked"] = []
    for chap_name, spec in expected_chapters.items():
        html_file = html_dir / f"{chap_name}.html"
        if html_file.is_file():
            content = html_file.read_text(encoding="utf-8")
            # Regex match clips
            clip_matches = re.findall(r'data-start="([\d\.]+)"\s+data-duration="([\d\.]+)"', content)
            details["html_files_checked"].append({
                "chapter": chap_name,
                "clip_count": len(clip_matches),
            })
        else:
            failures.append(AssertionFailure(
                module_id=module_id,
                module_name=name,
                assertion=f"Composition HTML file {html_file.name} exists",
                details=f"File not found: {html_file}",
            ))

    passed = len(failures) == 0
    return ModuleResult(
        module_id=module_id,
        name=name,
        passed=passed,
        duration_sec=time.time() - t0,
        message="Timeline duration 150.000s and 0 gaps verified" if passed else f"{len(failures)} timeline integrity failure(s)",
        details=details,
        failures=failures,
    )


# ---------------------------------------------------------------------------
# Module 4: Cut Count & Media Diversity
# ---------------------------------------------------------------------------

def check_cut_count_and_media_diversity(verbose: bool = False) -> ModuleResult:
    """Asserts >= 135 total cuts, >= 75 unique sources, 0 back-to-back duplicate sources, max repeat <= 2."""
    t0 = time.time()
    module_id = 4
    name = "cut_count_and_media_diversity"
    failures: list[AssertionFailure] = []
    details: dict[str, Any] = {}

    edl_path = COMMERCIAL_ROOT / "production" / "EDL-V7-PROPOSAL.json"
    if not edl_path.is_file():
        edl_path = COMMERCIAL_ROOT / "production" / "EDIT-DECISION-LIST.json"

    with open(edl_path, "r", encoding="utf-8") as f:
        edl_data = json.load(f)

    total_cuts = len(edl_data)
    details["total_cuts"] = total_cuts

    # 1. Minimum cut count >= 135
    if total_cuts < 135:
        failures.append(AssertionFailure(
            module_id=module_id,
            module_name=name,
            assertion="Total picture cuts >= 135",
            details=f"Found {total_cuts} cuts (minimum required: 135)",
            remediation="Ensure full beat-locked 143-cut EDL is integrated.",
        ))

    # 2. Minimum unique media sources >= 75
    sources = [cut["source"] for cut in edl_data if "source" in cut]
    unique_sources = set(sources)
    details["unique_sources_count"] = len(unique_sources)

    if len(unique_sources) < 75:
        failures.append(AssertionFailure(
            module_id=module_id,
            module_name=name,
            assertion="Unique media sources >= 75",
            details=f"Found {len(unique_sources)} unique sources (minimum required: 75)",
            remediation="Increase media diversity by incorporating vetted Flow pickups and site photos.",
        ))

    # 3. 0 back-to-back duplicate sources
    back_to_back_violations: list[dict[str, Any]] = []
    for i in range(len(sources) - 1):
        if sources[i] == sources[i + 1]:
            back_to_back_violations.append({
                "index": i,
                "source": sources[i],
                "cut_a_id": edl_data[i].get("id"),
                "cut_b_id": edl_data[i + 1].get("id"),
            })

    details["back_to_back_violations"] = back_to_back_violations
    if back_to_back_violations:
        failures.append(AssertionFailure(
            module_id=module_id,
            module_name=name,
            assertion="0 back-to-back duplicate sources",
            details=f"Found {len(back_to_back_violations)} back-to-back duplicate cuts: {back_to_back_violations[:3]}",
            remediation="Separate consecutive cuts of identical sources with an intervening cut or alternate angle.",
        ))

    # 4. Maximum repetition per source <= 2 across the entire film
    counts: dict[str, int] = {}
    for src in sources:
        counts[src] = counts.get(src, 0) + 1

    excess_repeats = {src: count for src, count in counts.items() if count > 2}
    details["excess_repeats"] = excess_repeats

    if excess_repeats:
        failures.append(AssertionFailure(
            module_id=module_id,
            module_name=name,
            assertion="Maximum repeat frequency <= 2 per source across 150s commercial",
            details=f"Sources used more than twice: {excess_repeats}",
            remediation="Replace excessive repeated media instances with alternative pickups from NEW-PICKUPS-CATALOG.json.",
        ))

    passed = len(failures) == 0
    return ModuleResult(
        module_id=module_id,
        name=name,
        passed=passed,
        duration_sec=time.time() - t0,
        message=f"{total_cuts} cuts across {len(unique_sources)} sources verified" if passed else f"{len(failures)} diversity violation(s)",
        details=details,
        failures=failures,
    )


# ---------------------------------------------------------------------------
# Module 5: Forbidden Asset Exclusions
# ---------------------------------------------------------------------------

def check_forbidden_asset_exclusions(verbose: bool = False) -> ModuleResult:
    """Verifies 0 out-of-region clips and 0 raw MLS survey-annotated photos."""
    t0 = time.time()
    module_id = 5
    name = "forbidden_asset_exclusions"
    failures: list[AssertionFailure] = []
    details: dict[str, Any] = {}

    # Forbidden list per R2 specification:
    # Out-of-region clips: 19-cascade, 20-flow, 21-explore, 10-restore, 22-envision, 22R-tropical-village
    forbidden_clips = [
        "19-cascade",
        "20-flow",
        "21-explore",
        "10-restore",
        "22-envision",
        "22R-tropical-village",
    ]

    # Raw MLS survey photos with baked-in annotations:
    forbidden_survey_photos = [
        "site-coastal-panorama.jpg",
        "site-ridge-view.jpg",
    ]

    details["forbidden_clips_rule"] = forbidden_clips
    details["forbidden_survey_photos_rule"] = forbidden_survey_photos

    # 1. Audit Active EDL
    edl_path = COMMERCIAL_ROOT / "production" / "EDL-V7-PROPOSAL.json"
    if not edl_path.is_file():
        edl_path = COMMERCIAL_ROOT / "production" / "EDIT-DECISION-LIST.json"

    with open(edl_path, "r", encoding="utf-8") as f:
        edl_data = json.load(f)

    edl_violations: list[dict[str, Any]] = []
    for cut in edl_data:
        src = cut.get("source", "")
        # Check out-of-region
        for fc in forbidden_clips:
            if fc in src:
                edl_violations.append({"type": "out_of_region", "cut_id": cut.get("id"), "source": src})
        # Check raw survey text
        for sp in forbidden_survey_photos:
            if sp in src:
                edl_violations.append({"type": "raw_survey_photo", "cut_id": cut.get("id"), "source": src})

    details["edl_violations"] = edl_violations
    if edl_violations:
        failures.append(AssertionFailure(
            module_id=module_id,
            module_name=name,
            assertion="EDL contains 0 forbidden out-of-region or raw survey-text assets",
            details=f"Found {len(edl_violations)} forbidden asset references in EDL: {edl_violations}",
            remediation="Replace survey-annotated photos (cuts 31, 44, 109, 111) with clean drone photos or Flow captures.",
        ))

    # 2. Audit Generated HTML compositions
    html_violations: list[dict[str, Any]] = []
    compositions_dir = COMMERCIAL_ROOT / "compositions"
    if compositions_dir.is_dir():
        for html_file in compositions_dir.glob("*.html"):
            content = html_file.read_text(encoding="utf-8")
            for fc in forbidden_clips:
                if fc in content:
                    html_violations.append({"file": html_file.name, "forbidden": fc})
            for sp in forbidden_survey_photos:
                if sp in content:
                    html_violations.append({"file": html_file.name, "forbidden": sp})

    details["html_violations"] = html_violations
    if html_violations:
        failures.append(AssertionFailure(
            module_id=module_id,
            module_name=name,
            assertion="Composition HTML files contain 0 forbidden asset references",
            details=f"Found {len(html_violations)} forbidden references in HTML files: {html_violations}",
            remediation="Regenerate chapter compositions with build_v7_compositions.py after updating EDL.",
        ))

    passed = len(failures) == 0
    return ModuleResult(
        module_id=module_id,
        name=name,
        passed=passed,
        duration_sec=time.time() - t0,
        message="0 forbidden out-of-region or survey-annotated assets found" if passed else f"{len(failures)} forbidden asset violation(s)",
        details=details,
        failures=failures,
    )


# ---------------------------------------------------------------------------
# Module 6: FFprobe Media Bounds & Internal Dissolve Windows
# ---------------------------------------------------------------------------

_FFPROBE_CACHE: dict[str, float] = {}

def _get_media_duration_ffprobe(file_path: Path) -> float | None:
    path_str = str(file_path.resolve())
    if path_str in _FFPROBE_CACHE:
        return _FFPROBE_CACHE[path_str]

    if not file_path.is_file():
        return None

    ffprobe_bin = shutil.which("ffprobe") or ("ffprobe.exe" if sys.platform == "win32" else "ffprobe")
    try:
        proc = subprocess.run(
            [
                ffprobe_bin,
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                str(file_path),
            ],
            capture_output=True,
            text=True,
            timeout=8,
        )
        if proc.returncode == 0:
            val = float(proc.stdout.strip())
            _FFPROBE_CACHE[path_str] = val
            return val
    except Exception:
        pass
    return None

def check_ffprobe_media_bounds_and_dissolves(verbose: bool = False) -> ModuleResult:
    """Probes all video cuts: source_start + dur * rate <= file_duration, and validates dissolve exclusions."""
    t0 = time.time()
    module_id = 6
    name = "ffprobe_media_bounds_and_dissolves"
    failures: list[AssertionFailure] = []
    details: dict[str, Any] = {}

    edl_path = COMMERCIAL_ROOT / "production" / "EDL-V7-PROPOSAL.json"
    if not edl_path.is_file():
        edl_path = COMMERCIAL_ROOT / "production" / "EDIT-DECISION-LIST.json"

    with open(edl_path, "r", encoding="utf-8") as f:
        edl_data = json.load(f)

    video_cuts: list[dict[str, Any]] = []
    image_extensions = {".jpg", ".jpeg", ".webp", ".png"}

    for cut in edl_data:
        src = cut.get("source", "")
        ext = Path(src).suffix.lower()
        if ext and ext not in image_extensions:
            video_cuts.append(cut)

    details["total_video_cuts"] = len(video_cuts)
    bound_violations: list[dict[str, Any]] = []
    dissolve_violations: list[dict[str, Any]] = []

    # Known internal dissolve intervals per survey findings:
    # 1. pickup-feet-beach-path-01.mp4: dissolve interval is 2.2s - 3.2s
    # 2. pickup-slicing-fruit-01.mp4: knife cut / dissolve in first 2.8s (< 2.8s)

    for cut in video_cuts:
        src = cut["source"]
        local_path = COMMERCIAL_ROOT / src
        if not local_path.is_file():
            # Try from workspace root
            local_path = WORKSPACE_ROOT / src

        if not local_path.is_file():
            failures.append(AssertionFailure(
                module_id=module_id,
                module_name=name,
                assertion=f"Video file exists on disk: {src}",
                details=f"Could not locate file: {local_path}",
            ))
            continue

        file_dur = _get_media_duration_ffprobe(local_path)
        if file_dur is None:
            failures.append(AssertionFailure(
                module_id=module_id,
                module_name=name,
                assertion=f"ffprobe extracts duration for {src}",
                details="ffprobe failed or returned empty output",
            ))
            continue

        source_start = float(cut.get("source_start", 0.0))
        cut_dur = float(cut["duration"])
        playback_rate = float(cut.get("playback_rate", 1.0))
        required_src_dur = source_start + (cut_dur * playback_rate)

        # Allow 0.02s epsilon for float rounding
        if required_src_dur > (file_dur + 0.02):
            bound_violations.append({
                "cut_id": cut.get("id"),
                "source": src,
                "source_start": source_start,
                "needed_end": required_src_dur,
                "file_duration": file_dur,
                "overflow": required_src_dur - file_dur,
            })

        # Check internal dissolve intervals
        cut_source_end = source_start + (cut_dur * playback_rate)
        if "pickup-feet-beach-path-01" in src:
            # Overlaps [2.2, 3.2]?
            overlap_start = max(source_start, 2.2)
            overlap_end = min(cut_source_end, 3.2)
            if overlap_start < overlap_end:
                dissolve_violations.append({
                    "cut_id": cut.get("id"),
                    "source": src,
                    "window": [source_start, cut_source_end],
                    "dissolve_window": [2.2, 3.2],
                })

        if "pickup-slicing-fruit-01" in src:
            # Overlaps < 2.8s?
            if source_start < 2.8:
                dissolve_violations.append({
                    "cut_id": cut.get("id"),
                    "source": src,
                    "window": [source_start, cut_source_end],
                    "dissolve_window": [0.0, 2.8],
                })

    details["bound_violations"] = bound_violations
    details["dissolve_violations"] = dissolve_violations

    if bound_violations:
        failures.append(AssertionFailure(
            module_id=module_id,
            module_name=name,
            assertion="All video cuts satisfy source_start + dur * rate <= file_duration",
            details=f"Found {len(bound_violations)} cuts exceeding file duration: {bound_violations[:3]}",
            remediation="Trim cut durations or shift source_start to stay within actual media boundaries.",
        ))

    if dissolve_violations:
        failures.append(AssertionFailure(
            module_id=module_id,
            module_name=name,
            assertion="Video cuts avoid known internal clip dissolve intervals",
            details=f"Found {len(dissolve_violations)} cuts cutting into internal dissolves: {dissolve_violations}",
            remediation="Reframe cut windows for pickup-feet-beach-path-01 and pickup-slicing-fruit-01 per catalog specs.",
        ))

    passed = len(failures) == 0
    return ModuleResult(
        module_id=module_id,
        name=name,
        passed=passed,
        duration_sec=time.time() - t0,
        message=f"{len(video_cuts)} video cuts verified against ffprobe bounds" if passed else f"{len(failures)} media bounds violation(s)",
        details=details,
        failures=failures,
    )


# ---------------------------------------------------------------------------
# Module 7: Seek-Safe GSAP Transforms
# ---------------------------------------------------------------------------

def check_seek_safe_gsap_transforms(verbose: bool = False) -> ModuleResult:
    """Verifies 100% of static image cuts (<img>) have seek-safe fromTo transforms with immediateRender: false."""
    t0 = time.time()
    module_id = 7
    name = "seek_safe_gsap_transforms"
    failures: list[AssertionFailure] = []
    details: dict[str, Any] = {}

    chapter_files = [
        COMMERCIAL_ROOT / "compositions" / f"{ch}.html"
        for ch in ["place", "basis", "lots", "water", "close"]
    ]

    total_image_cuts = 0
    verified_image_tweens = 0
    missing_image_tweens: list[dict[str, Any]] = []
    immediate_render_violations: list[str] = []

    for html_file in chapter_files:
        if not html_file.is_file():
            failures.append(AssertionFailure(
                module_id=module_id,
                module_name=name,
                assertion=f"Chapter file {html_file.name} exists",
                details=f"File not found: {html_file}",
            ))
            continue

        content = html_file.read_text(encoding="utf-8")

        # Find all <img> elements inside .picture divs
        img_ids = re.findall(r'<img\s+id="([^"]+)"', content)
        total_image_cuts += len(img_ids)

        for i_id in img_ids:
            # Expected pattern in timeline: tl.fromTo("#{i_id}", ... immediateRender: false ...)
            pattern = re.compile(
                rf'tl\.fromTo\(\s*["\']#{re.escape(i_id)}["\'].*?immediateRender\s*:\s*false',
                re.DOTALL
            )
            if pattern.search(content):
                verified_image_tweens += 1
            else:
                missing_image_tweens.append({"file": html_file.name, "image_id": i_id})

        # Check all tl.fromTo calls across the file for immediateRender: false
        all_from_tos = re.findall(r'tl\.fromTo\((.*?)\);', content, re.DOTALL)
        for ft in all_from_tos:
            if "immediateRender" not in ft or "immediateRender:false" not in ft.replace(" ", ""):
                immediate_render_violations.append(ft[:80].strip())

    details["total_image_cuts"] = total_image_cuts
    details["verified_image_tweens"] = verified_image_tweens
    details["missing_image_tweens"] = missing_image_tweens
    details["immediate_render_violations_count"] = len(immediate_render_violations)

    if missing_image_tweens:
        failures.append(AssertionFailure(
            module_id=module_id,
            module_name=name,
            assertion="100% of static image cuts have GSAP fromTo Ken Burns transforms with immediateRender: false",
            details=f"Found {len(missing_image_tweens)} image cuts missing seek-safe fromTo tweens: {missing_image_tweens[:3]}",
            remediation="Ensure build_v7_compositions.py generates Ken Burns fromTo tweens for all <img> tags.",
        ))

    if immediate_render_violations:
        failures.append(AssertionFailure(
            module_id=module_id,
            module_name=name,
            assertion="All GSAP fromTo tweens specify immediateRender: false",
            details=f"Found {len(immediate_render_violations)} fromTo tweens missing immediateRender: false: {immediate_render_violations[:3]}",
            remediation="Add `immediateRender: false` to all GSAP fromTo tweens to prevent ghost states during scrubber seeks.",
        ))

    passed = len(failures) == 0
    return ModuleResult(
        module_id=module_id,
        name=name,
        passed=passed,
        duration_sec=time.time() - t0,
        message=f"All {total_image_cuts} static image cuts have seek-safe fromTo transforms" if passed else f"{len(failures)} seek-safe transform violation(s)",
        details=details,
        failures=failures,
    )


# ---------------------------------------------------------------------------
# Module 8: Transition Ledger Verification
# ---------------------------------------------------------------------------

def check_transition_ledger_count(verbose: bool = False) -> ModuleResult:
    """Verifies production/TRANSITION-LEDGER.json contains >= 75 verified transitions bound to active cut boundaries."""
    t0 = time.time()
    module_id = 8
    name = "transition_ledger_count"
    failures: list[AssertionFailure] = []
    details: dict[str, Any] = {}

    ledger_path = COMMERCIAL_ROOT / "production" / "TRANSITION-LEDGER.json"
    if not ledger_path.is_file():
        failures.append(AssertionFailure(
            module_id=module_id,
            module_name=name,
            assertion="TRANSITION-LEDGER.json exists",
            details=f"File not found: {ledger_path}",
            remediation="Run build_v7_compositions.py to generate TRANSITION-LEDGER.json.",
        ))
        return ModuleResult(
            module_id=module_id,
            name=name,
            passed=False,
            duration_sec=time.time() - t0,
            message="TRANSITION-LEDGER.json not found",
            details=details,
            failures=failures,
        )

    with open(ledger_path, "r", encoding="utf-8") as f:
        try:
            ledger_data = json.load(f)
        except Exception as exc:
            failures.append(AssertionFailure(
                module_id=module_id,
                module_name=name,
                assertion="TRANSITION-LEDGER.json is valid JSON",
                details=str(exc),
            ))
            return ModuleResult(module_id=module_id, name=name, passed=False, duration_sec=time.time() - t0, message="Corrupted ledger JSON", failures=failures)

    transition_count = len(ledger_data)
    details["transition_count"] = transition_count

    # 1. Assert >= 75 transitions
    if transition_count < 75:
        failures.append(AssertionFailure(
            module_id=module_id,
            module_name=name,
            assertion="TRANSITION-LEDGER.json contains >= 75 verified transitions",
            details=f"Found {transition_count} transitions in ledger (minimum required: 75)",
            remediation="Upgrade build_v7_compositions.py with dynamic cut boundary binding to snap transitions to active V7 cuts.",
        ))

    # 2. Check schema and fields
    required_keys = {"time", "chapter", "method", "from_source", "to_source", "camera_motion", "fx_layer"}
    malformed_entries = []
    for idx, item in enumerate(ledger_data):
        missing = required_keys - set(item.keys())
        if missing:
            malformed_entries.append({"index": idx, "missing_keys": list(missing)})

    details["malformed_entries"] = malformed_entries
    if malformed_entries:
        failures.append(AssertionFailure(
            module_id=module_id,
            module_name=name,
            assertion="All transition ledger entries contain required metadata fields",
            details=f"Found {len(malformed_entries)} malformed entries: {malformed_entries[:3]}",
        ))

    # 3. Check active cut boundary binding against EDL
    edl_path = COMMERCIAL_ROOT / "production" / "EDL-V7-PROPOSAL.json"
    if not edl_path.is_file():
        edl_path = COMMERCIAL_ROOT / "production" / "EDIT-DECISION-LIST.json"

    with open(edl_path, "r", encoding="utf-8") as f:
        edl_data = json.load(f)

    edl_cut_starts = [float(cut["start"]) for cut in edl_data]
    unbound_transitions = []

    for item in ledger_data:
        t_time = float(item["time"])
        # Check if t_time is within 0.45s of any cut start
        closest_delta = min(abs(t_time - c_start) for c_start in edl_cut_starts)
        if closest_delta > 0.45:
            unbound_transitions.append({"transition": item.get("number"), "time": t_time, "delta": closest_delta})

    details["unbound_transitions"] = unbound_transitions
    if unbound_transitions:
        failures.append(AssertionFailure(
            module_id=module_id,
            module_name=name,
            assertion="All ledger transitions actively bind to V7 cut boundaries (<0.45s tolerance)",
            details=f"Found {len(unbound_transitions)} transitions drifting from active cut boundaries: {unbound_transitions[:3]}",
            remediation="Synchronize curated transition timestamps with active V7 cut start times.",
        ))

    passed = len(failures) == 0
    return ModuleResult(
        module_id=module_id,
        name=name,
        passed=passed,
        duration_sec=time.time() - t0,
        message=f"{transition_count} transitions verified in ledger" if passed else f"{len(failures)} transition ledger failure(s)",
        details=details,
        failures=failures,
    )


# ---------------------------------------------------------------------------
# Module 9: HyperFrames Standards & Contrast Check
# ---------------------------------------------------------------------------

def _srgb_to_linear(val: float) -> float:
    c = val / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

def _hex_to_luminance(hex_str: str) -> float:
    h = hex_str.lstrip("#")
    r = int(h[0:2], 16)
    g = int(h[2:4], 16)
    b = int(h[4:6], 16)
    return 0.2126 * _srgb_to_linear(r) + 0.7152 * _srgb_to_linear(g) + 0.0722 * _srgb_to_linear(b)

def _contrast_ratio(hex1: str, hex2: str) -> float:
    l1 = _hex_to_luminance(hex1)
    l2 = _hex_to_luminance(hex2)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)

def check_hyperframes_standards_and_contrast(skip_browser: bool = False, verbose: bool = False) -> ModuleResult:
    """Runs npx hyperframes check ensuring 0 errors, 0 motion warnings, and 100% WCAG AA contrast pass."""
    t0 = time.time()
    module_id = 9
    name = "hyperframes_standards_and_contrast"
    failures: list[AssertionFailure] = []
    details: dict[str, Any] = {}

    # 1. Mathematical Contrast Verification for Executive Investor Palette
    bg_green = "#142c25"
    cream_text = "#f4efe4"
    gold_accent = "#d9be84"

    contrast_cream = _contrast_ratio(bg_green, cream_text)
    contrast_gold = _contrast_ratio(bg_green, gold_accent)

    details["contrast_cream_vs_green"] = round(contrast_cream, 2)
    details["contrast_gold_vs_green"] = round(contrast_gold, 2)

    # WCAG AA requires 4.5:1 for normal text, 3.0:1 for large text. AAA requires 7.0:1.
    if contrast_cream < 4.5:
        failures.append(AssertionFailure(
            module_id=module_id,
            module_name=name,
            assertion="Cream text (#f4efe4) against emerald (#142c25) passes WCAG AA (>=4.5:1)",
            details=f"Calculated contrast ratio: {contrast_cream:.2f}:1",
        ))

    if contrast_gold < 4.5:
        failures.append(AssertionFailure(
            module_id=module_id,
            module_name=name,
            assertion="Gold accent (#d9be84) against emerald (#142c25) passes WCAG AA (>=4.5:1)",
            details=f"Calculated contrast ratio: {contrast_gold:.2f}:1",
        ))

    # 2. Automated Headless Browser Check via `npx hyperframes check --json`
    if skip_browser:
        details["browser_check_skipped"] = True
    else:
        npx_bin = shutil.which("npx") or ("npx.cmd" if sys.platform == "win32" else "npx")
        try:
            proc = subprocess.run(
                [npx_bin, "hyperframes", "check", "--json"],
                capture_output=True,
                text=True,
                timeout=120,
                cwd=str(COMMERCIAL_ROOT),
            )
            stdout = proc.stdout.strip()
            stderr = proc.stderr.strip()

            # Parse JSON report
            # Find the JSON envelope starting with '{'
            json_start = stdout.find("{")
            if json_start != -1:
                json_str = stdout[json_start:]
                report = json.loads(json_str)
                details["hyperframes_check_report"] = {
                    "ok": report.get("ok"),
                    "runtime_errors": report.get("runtime", {}).get("errorCount", 0),
                    "layout_errors": report.get("layout", {}).get("errorCount", 0),
                    "motion_errors": report.get("motion", {}).get("errorCount", 0),
                    "contrast_checked": report.get("contrast", {}).get("checked", 0),
                    "contrast_passed": report.get("contrast", {}).get("passed", 0),
                }

                # Assertions on HyperFrames check output
                runtime_errors = report.get("runtime", {}).get("errorCount", 0)
                layout_errors = report.get("layout", {}).get("errorCount", 0)
                motion_errors = report.get("motion", {}).get("errorCount", 0)
                contrast_checked = report.get("contrast", {}).get("checked", 0)
                contrast_passed = report.get("contrast", {}).get("passed", 0)

                if runtime_errors > 0:
                    failures.append(AssertionFailure(
                        module_id=module_id,
                        module_name=name,
                        assertion="HyperFrames check has 0 runtime errors",
                        details=f"Runtime errors: {runtime_errors}, findings: {report.get('runtime', {}).get('findings')}",
                    ))

                if layout_errors > 0:
                    failures.append(AssertionFailure(
                        module_id=module_id,
                        module_name=name,
                        assertion="HyperFrames check has 0 layout collisions",
                        details=f"Layout errors: {layout_errors}, findings: {report.get('layout', {}).get('findings')}",
                    ))

                if motion_errors > 0:
                    failures.append(AssertionFailure(
                        module_id=module_id,
                        module_name=name,
                        assertion="HyperFrames check has 0 motion errors",
                        details=f"Motion errors: {motion_errors}",
                    ))

                if contrast_checked > 0 and contrast_passed < contrast_checked:
                    failures.append(AssertionFailure(
                        module_id=module_id,
                        module_name=name,
                        assertion="HyperFrames check has 100% contrast pass",
                        details=f"Passed {contrast_passed} / {contrast_checked} text contrast checks",
                    ))

            else:
                failures.append(AssertionFailure(
                    module_id=module_id,
                    module_name=name,
                    assertion="npx hyperframes check emits JSON output",
                    details=f"stdout snippet: {stdout[:300]}, stderr: {stderr[:300]}",
                ))

        except subprocess.TimeoutExpired:
            failures.append(AssertionFailure(
                module_id=module_id,
                module_name=name,
                assertion="npx hyperframes check completes within 60s",
                details="Browser check process timed out",
            ))
        except Exception as exc:
            failures.append(AssertionFailure(
                module_id=module_id,
                module_name=name,
                assertion="npx hyperframes check executes successfully",
                details=str(exc),
            ))

    passed = len(failures) == 0
    return ModuleResult(
        module_id=module_id,
        name=name,
        passed=passed,
        duration_sec=time.time() - t0,
        message="HyperFrames standards and 100% contrast verified" if passed else f"{len(failures)} standards/contrast failure(s)",
        details=details,
        failures=failures,
    )


# ---------------------------------------------------------------------------
# Module 10: Studio Preview Server Health
# ---------------------------------------------------------------------------

def check_studio_preview_health(port: int = 3003, verbose: bool = False) -> ModuleResult:
    """Verifies Studio preview server on port 3003 returns HTTP 200 OK without disrupting the process."""
    t0 = time.time()
    module_id = 10
    name = "studio_preview_health"
    failures: list[AssertionFailure] = []
    details: dict[str, Any] = {}

    target_url = f"http://localhost:{port}/eden-mazara-commercial/index.html"
    root_url = f"http://localhost:{port}/"
    details["target_url"] = target_url
    details["root_url"] = root_url

    # Check composition index.html endpoint
    try:
        req = urllib.request.Request(target_url, headers={"User-Agent": "HyperFrames-Verification/7.0"})
        with urllib.request.urlopen(req, timeout=4) as response:
            status = response.status
            content = response.read(2048).decode("utf-8", errors="replace")
            details["composition_status"] = status
            details["composition_content_sample"] = content[:150]

            if status != 200:
                failures.append(AssertionFailure(
                    module_id=module_id,
                    module_name=name,
                    assertion=f"GET {target_url} returns 200 OK",
                    details=f"Received status code: {status}",
                ))

            if len(content) < 200 or "<html" not in content.lower():
                failures.append(AssertionFailure(
                    module_id=module_id,
                    module_name=name,
                    assertion=f"{target_url} serves valid HTML composition",
                    details=f"Response content too short or missing <html>: {content[:100]}",
                ))

    except urllib.error.URLError as err:
        failures.append(AssertionFailure(
            module_id=module_id,
            module_name=name,
            assertion=f"Preview server is listening on port {port}",
            details=f"Connection error: {err}",
            remediation=f"Ensure HyperFrames Studio preview is running at port {port} (e.g. PID 37792). Do not kill or restart.",
        ))
    except Exception as exc:
        failures.append(AssertionFailure(
            module_id=module_id,
            module_name=name,
            assertion=f"GET {target_url} succeeds without exception",
            details=str(exc),
        ))

    # Check Studio root shell endpoint
    try:
        req_root = urllib.request.Request(root_url, headers={"User-Agent": "HyperFrames-Verification/7.0"})
        with urllib.request.urlopen(req_root, timeout=4) as response_root:
            details["root_status"] = response_root.status
            if response_root.status != 200:
                failures.append(AssertionFailure(
                    module_id=module_id,
                    module_name=name,
                    assertion=f"GET {root_url} returns 200 OK",
                    details=f"Received status code: {response_root.status}",
                ))
    except Exception as exc:
        details["root_check_warning"] = str(exc)

    passed = len(failures) == 0
    return ModuleResult(
        module_id=module_id,
        name=name,
        passed=passed,
        duration_sec=time.time() - t0,
        message=f"Studio preview server on port {port} is healthy (HTTP 200 OK)" if passed else "Studio preview health check failed",
        details=details,
        failures=failures,
    )


# ---------------------------------------------------------------------------
# Visual Snapshot QA Runner (Optional / Integration)
# ---------------------------------------------------------------------------

def run_visual_snapshot_qa() -> tuple[bool, str]:
    """Captures and verifies visual snapshots at chapter midpoints."""
    timestamps = "15.0,45.0,77.5,110.0,137.5"
    npx_bin = shutil.which("npx") or ("npx.cmd" if sys.platform == "win32" else "npx")
    cmd = [npx_bin, "hyperframes", "snapshot", "--at", timestamps, "--no-end"]
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(COMMERCIAL_ROOT),
        )
        if proc.returncode == 0:
            return True, f"Visual snapshots captured cleanly at t={timestamps}"
        return False, f"Snapshot command failed: {proc.stderr[:200]}"
    except Exception as exc:
        return False, str(exc)


# ---------------------------------------------------------------------------
# Suite Runner & CLI
# ---------------------------------------------------------------------------

def run_suite(
    skip_browser: bool = False,
    skip_cli: bool = False,
    take_snapshots: bool = False,
    selected_module: str | None = None,
    verbose: bool = False,
) -> VerificationSuiteReport:
    """Orchestrates execution of the 10 verification modules."""
    t_start = time.time()
    modules_to_run: list[tuple[int, str, Any]] = [
        (1, "cli_subcommands", lambda: check_cli_subcommands(verbose=verbose)),
        (2, "workspace_hardlink_hygiene", lambda: check_workspace_hardlink_hygiene(verbose=verbose)),
        (3, "timeline_duration_and_gaps", lambda: check_timeline_duration_and_gaps(verbose=verbose)),
        (4, "cut_count_and_media_diversity", lambda: check_cut_count_and_media_diversity(verbose=verbose)),
        (5, "forbidden_asset_exclusions", lambda: check_forbidden_asset_exclusions(verbose=verbose)),
        (6, "ffprobe_media_bounds_and_dissolves", lambda: check_ffprobe_media_bounds_and_dissolves(verbose=verbose)),
        (7, "seek_safe_gsap_transforms", lambda: check_seek_safe_gsap_transforms(verbose=verbose)),
        (8, "transition_ledger_count", lambda: check_transition_ledger_count(verbose=verbose)),
        (9, "hyperframes_standards_and_contrast", lambda: check_hyperframes_standards_and_contrast(skip_browser=skip_browser, verbose=verbose)),
        (10, "studio_preview_health", lambda: check_studio_preview_health(verbose=verbose)),
    ]

    results: list[ModuleResult] = []

    for mod_id, mod_name, mod_fn in modules_to_run:
        # Filter if --module was specified
        if selected_module:
            if str(mod_id) != selected_module and selected_module.lower() not in mod_name.lower():
                continue

        # Skip CLI if requested
        if mod_id == 1 and skip_cli:
            continue

        try:
            res = mod_fn()
            results.append(res)
        except Exception as exc:
            results.append(ModuleResult(
                module_id=mod_id,
                name=mod_name,
                passed=False,
                duration_sec=0.0,
                message=f"Unhandled exception in verification module: {exc}",
                failures=[AssertionFailure(
                    module_id=mod_id,
                    module_name=mod_name,
                    assertion="Module executes without unhandled exception",
                    details=str(exc),
                )],
            ))

    if take_snapshots and not skip_browser:
        snap_ok, snap_msg = run_visual_snapshot_qa()
        if not snap_ok:
            results.append(ModuleResult(
                module_id=11,
                name="visual_snapshots",
                passed=False,
                duration_sec=0.0,
                message=snap_msg,
                failures=[AssertionFailure(
                    module_id=11,
                    module_name="visual_snapshots",
                    assertion="Visual snapshot capture succeeds",
                    details=snap_msg,
                )],
            ))

    total_modules = len(results)
    passed_modules = sum(1 for r in results if r.passed)
    failed_modules = total_modules - passed_modules
    all_passed = (failed_modules == 0)

    report = VerificationSuiteReport(
        timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        all_passed=all_passed,
        total_modules=total_modules,
        passed_modules=passed_modules,
        failed_modules=failed_modules,
        duration_sec=round(time.time() - t_start, 3),
        modules=results,
    )
    return report


def print_human_report(report: VerificationSuiteReport, verbose: bool = False) -> None:
    """Renders formatted console output for the verification report."""
    print("=" * 80)
    print("EDEN MAZARA COMMERCIAL V7 — AUTOMATED OPAQUE-BOX VERIFICATION SUITE")
    print(f"Timestamp: {report.timestamp} | Total Duration: {report.duration_sec:.2f}s")
    print("=" * 80)

    for mod in report.modules:
        status_tag = "[PASS]" if mod.passed else "[FAIL]"
        print(f"\n{status_tag} Module {mod.module_id:02d}: {mod.name} ({mod.duration_sec:.2f}s)")
        print(f"       Summary: {mod.message}")

        if not mod.passed and mod.failures:
            print("       Failures:")
            for f in mod.failures:
                print(f"         - Assertion: {f.assertion}")
                print(f"           Details:   {f.details}")
                if f.remediation:
                    print(f"           Remedy:    {f.remediation}")

        if verbose and mod.details:
            print("       Diagnostic Details:")
            for k, v in mod.details.items():
                v_str = str(v)
                if len(v_str) > 100:
                    v_str = v_str[:97] + "..."
                print(f"         * {k}: {v_str}")

    print("\n" + "=" * 80)
    if report.all_passed:
        print(f"OVERALL STATUS: PASS (100%) — All {report.passed_modules}/{report.total_modules} modules verified.")
    else:
        print(f"OVERALL STATUS: FAIL — {report.failed_modules}/{report.total_modules} modules failed verification.")
    print("=" * 80)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Automated Opaque-Box Verification Test Suite for Eden Mazara 2:30 Commercial V7",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--fast", "--skip-browser", dest="skip_browser", action="store_true", help="Skip headless browser check and snapshots")
    parser.add_argument("--skip-snapshots", dest="skip_snapshots", action="store_true", help="Skip visual snapshot generation")
    parser.add_argument("--snapshots", dest="take_snapshots", action="store_true", help="Force capture and verification of visual snapshots")
    parser.add_argument("--skip-cli", dest="skip_cli", action="store_true", help="Skip flow-cli verification")
    parser.add_argument("--module", dest="selected_module", type=str, default=None, help="Run only specific module (e.g. 2, 7, hardlink)")
    parser.add_argument("--json", dest="json_mode", action="store_true", help="Output machine-readable JSON envelope")
    parser.add_argument("--verbose", "-v", dest="verbose", action="store_true", help="Show diagnostic details")

    args = parser.parse_args()

    report = run_suite(
        skip_browser=args.skip_browser,
        skip_cli=args.skip_cli,
        take_snapshots=args.take_snapshots and not args.skip_snapshots,
        selected_module=args.selected_module,
        verbose=args.verbose,
    )

    if args.json_mode:
        print(json.dumps(asdict(report), indent=2))
    else:
        print_human_report(report, verbose=args.verbose)

    return 0 if report.all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
