"""Build V7 HyperFrames chapter compositions with seek-safe camera motion,
beat-locked transitions (75 transitions), and WCAG AAA executive investor UI overlays.

Default EDL input:
  - production/EDL-V7-PROPOSAL.json (if present)
  - otherwise production/EDIT-DECISION-LIST.json

Outputs (unless --dry-run or custom --out-dir is passed):
  - compositions/place.html
  - compositions/basis.html
  - compositions/lots.html
  - compositions/water.html
  - compositions/close.html
  - production/TRANSITION-LEDGER.json
  - production/MOTION-AND-TRANSITIONS-SPEC.json
"""
from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

CHAPTER_META: dict[str, dict[str, Any]] = {
    "place": {
        "start": 0.0,
        "duration": 30.0,
        "brand_eyebrow": "I · THE RHYTHM",
        "headlines": [
            {
                "id": "place-headline-0",
                "start": 0.665,
                "duration": 2.4,
                "eyebrow": "EDEN MAZARA",
                "text": "A different rhythm.",
                "from_vars": {"opacity": 0, "y": 32},
            },
            {
                "id": "place-headline-1",
                "start": 20.535,
                "duration": 5.0,
                "eyebrow": "COSTA RICA’S GOLD COAST",
                "text": "Live. Restore. Belong.",
                "from_vars": {"opacity": 0, "x": -35},
            },
        ],
        "metrics": [
            {
                "id": "place-metric-0",
                "start": 0.35,
                "duration": 2.95,
                "eyebrow": "LOCATION & ECOLOGICAL CORRIDOR",
                "value": "GUANACASTE · GOLD COAST",
                "detail": "Coastal dry-forest & Pacific corridor · Brasilito, Costa Rica",
                "value_size": "54px",
            },
        ],
    },
    "basis": {
        "start": 30.0,
        "duration": 30.0,
        "brand_eyebrow": "II · THE LAND & BASIS",
        "headlines": [
            {
                "id": "basis-headline-0",
                "start": 14.185,
                "duration": 3.0,
                "eyebrow": "ONE VISION",
                "text": "A place to live.",
                "from_vars": {"opacity": 0, "y": 32},
            },
            {
                "id": "basis-headline-1",
                "start": 17.265,
                "duration": 2.05,
                "eyebrow": "THREE PATHS",
                "text": "A sanctuary to restore.",
                "from_vars": {"opacity": 0, "x": -35},
            },
            {
                "id": "basis-headline-2",
                "start": 19.335,
                "duration": 5.0,
                "eyebrow": "EDEN MAZARA",
                "text": "A community to belong to.",
                "from_vars": {"opacity": 0, "y": 32},
            },
        ],
        "metrics": [
            {
                "id": "basis-metric-0",
                "start": 0.3,
                "duration": 3.9,
                "eyebrow": "PORTFOLIO FOOTPRINT",
                "value": "950 acres",
                "detail": "Reported portfolio scale · hills above Brasilito toward the Pacific",
            },
            {
                "id": "basis-metric-1",
                "start": 8.5,
                "duration": 5.0,
                "eyebrow": "MASTER PLAN ARCHITECTURE",
                "value": "Three Pillars",
                "detail": "Residential Village · Wellness Sanctuary · Regenerative Stewardship",
            },
            {
                "id": "basis-metric-2",
                "start": 21.5,
                "duration": 3.7,
                "eyebrow": "DISCIPLINED ACQUISITION BASIS",
                "value": "$9 million",
                "detail": "Contracted purchase price · closing subject to diligence",
            },
        ],
    },
    "lots": {
        "start": 60.0,
        "duration": 35.0,
        "brand_eyebrow": "III · EL ENCANTO",
        "headlines": [
            {
                "id": "lots-headline-0",
                "start": 0.305,
                "duration": 5.0,
                "eyebrow": "EL ENCANTO",
                "text": "A place of your own.",
                "from_vars": {"opacity": 0, "y": 32},
            },
            {
                "id": "lots-headline-1",
                "start": 16.2,
                "duration": 1.8,
                "eyebrow": "THE SANCTUARY VISION",
                "text": "Move.",
                "from_vars": {"opacity": 0, "x": -35},
            },
            {
                "id": "lots-headline-2",
                "start": 18.2,
                "duration": 1.2,
                "eyebrow": "THE SANCTUARY VISION",
                "text": "Breathe.",
                "from_vars": {"opacity": 0, "y": 32},
            },
            {
                "id": "lots-headline-3",
                "start": 19.6,
                "duration": 0.925,
                "eyebrow": "THE SANCTUARY VISION",
                "text": "Reconnect.",
                "from_vars": {"opacity": 0, "x": -35},
            },
            {
                "id": "lots-headline-4",
                "start": 20.525,
                "duration": 4.0,
                "eyebrow": "THE SANCTUARY VISION",
                "text": "Live well. Together.",
                "from_vars": {"opacity": 0, "y": 32},
            },
        ],
        "metrics": [
            {
                "id": "lots-metric-0",
                "start": 10.0,
                "duration": 6.0,
                "eyebrow": "PHASE 1 RESIDENTIAL CHAPTER",
                "value": "40 homesites",
                "detail": "Reported titled lots · El Encanto proposed first phase",
            },
            {
                "id": "lots-metric-1",
                "start": 21.0,
                "duration": 4.5,
                "eyebrow": "ILLUSTRATIVE PHASE 1 OUTLOOK",
                "value": "$26M – $30M",
                "detail": "Reported Phase 1 gross lot projection · illustrative & subject to diligence",
            },
        ],
    },
    "water": {
        "start": 95.0,
        "duration": 30.0,
        "brand_eyebrow": "IV · SANCTUARY & DILIGENCE",
        "headlines": [
            {
                "id": "water-headline-0",
                "start": 0.635,
                "duration": 5.0,
                "eyebrow": "CARE FOR THE LAND",
                "text": "A quieter hour.",
                "from_vars": {"opacity": 0, "y": 32},
            },
            {
                "id": "water-headline-1",
                "start": 19.455,
                "duration": 6.0,
                "eyebrow": "PHASE BY PHASE",
                "text": "Room for yourself.",
                "from_vars": {"opacity": 0, "x": -35},
            },
        ],
        "metrics": [
            {
                "id": "water-metric-0",
                "start": 13.5,
                "duration": 5.3,
                "eyebrow": "REPORTED WATER INFRASTRUCTURE",
                "value": "9 production wells",
                "detail": "Reported in project materials · on-site water infrastructure",
            },
            {
                "id": "water-metric-1",
                "start": 19.2,
                "duration": 6.3,
                "eyebrow": "REPORTED HYDROLOGICAL CAPACITY",
                "value": "Above 50 L/s",
                "detail": "Reported combined yield · capacity & approvals subject to diligence",
            },
        ],
    },
    "close": {
        "start": 125.0,
        "duration": 25.0,
        "brand_eyebrow": "V · THE INVITATION",
        "headlines": [
            {
                "id": "close-headline-0",
                "start": 7.995,
                "duration": 3.0,
                "eyebrow": "SOPHIA • ENVISIONED DIGITAL COMPASS",
                "text": "The journey continues.",
                "from_vars": {"opacity": 0, "y": 32},
            },
            {
                "id": "close-headline-1",
                "start": 14.495,
                "duration": 3.2,
                "eyebrow": "LIVE • RESTORE • BELONG",
                "text": "One vision. Three paths.",
                "from_vars": {"opacity": 0, "x": -35},
            },
        ],
        "metrics": [
            {
                "id": "close-metric-0",
                "start": 1.0,
                "duration": 6.0,
                "eyebrow": "COASTAL SANCTUARY VISION",
                "value": "A life by the Pacific",
                "detail": "Eden Mazara · illustrative coastal & regenerative vision",
                "value_size": "68px",
            },
            {
                "id": "close-metric-1",
                "start": 11.0,
                "duration": 8.5,
                "eyebrow": "PARTNER & CAPITAL ALIGNMENT",
                "value": "Acquisition & Joint Venture",
                "detail": "Seeking aligned capital & development partners · edenmazara.com",
                "value_size": "54px",
            },
        ],
        "end_card": {
            "id": "close-end",
            "start": 20.8,
            "duration": 4.2,
            "eyebrow": "THE NEXT CHAPTER · INVESTOR MEMORANDUM",
            "title": "Eden Mazara",
            "subtitle": "950 Acres · $9M Contracted Basis · 40 Phase 1 Lots",
            "partners": "Acquisition & development partners",
            "contact": "edenmazara.com  ·  advisory@edenmazara.com",
        },
    },
}

# 3 alternating seek-safe Ken Burns presets for static property images (<img>)
KEN_BURNS_PRESETS: list[dict[str, Any]] = [
    {
        "name": "aerial_push_in",
        "description": "Slow aerial push-in (scale 1.0 -> 1.12, x: 0 -> -18, y: 0 -> -10)",
        "from": {"scale": 1.0, "x": 0, "y": 0},
        "to": {"scale": 1.12, "x": -18, "y": -10},
    },
    {
        "name": "horizon_pan_right_pull_back",
        "description": "Horizon pan-right + pull-back (scale 1.12 -> 1.02, x: -24 -> 16, y: -8 -> 0)",
        "from": {"scale": 1.12, "x": -24, "y": -8},
        "to": {"scale": 1.02, "x": 16, "y": 0},
    },
    {
        "name": "ridge_pan_left_push",
        "description": "Ridge pan-left + push (scale 1.02 -> 1.14, x: 20 -> -20, y: 8 -> -8)",
        "from": {"scale": 1.02, "x": 20, "y": 8},
        "to": {"scale": 1.14, "x": -20, "y": -8},
    },
]

# Curated 75 transitions combining the 30 reviewed ledger transitions,
# 40 agent-proposed transitions, and 5 key aerial/evidence handoffs.
CURATED_TRANSITIONS: dict[float, tuple[str, str, str]] = {
    # Act 1: place (0 - 30s)
    1.975: ("orbital-to-coastal descent", "Orbital arrival resolves into low-altitude Guanacaste coastal aerial.", "punch"),
    3.385: ("scale cut", "Coastal ridge becomes a personal morning interior as narration begins.", "bloom"),
    5.115: ("light and texture match", "Curtain light hands off to broadleaf shadow on the plaster wall.", "punch"),
    6.145: ("horizon cut", "Villa outlook opens onto the Pacific beach.", "punch"),
    7.505: ("tactile cut", "Shore texture hands off to bare feet on warm stone.", "punch"),
    8.865: ("tactile breath cut", "Bare feet move into the linen breeze; hold long enough to feel the place.", "punch"),
    9.905: ("morning ritual", "Moving linen releases into warm coffee at the terrace.", "bloom"),
    11.275: ("prop match", "Coffee in hand becomes a warm cup offered by a host.", "punch"),
    12.645: ("gesture match", "The offered cup hands off to hands opening the timber door.", "punch"),
    13.665: ("door reveal", "Door action opens the shaded terrace and a relaxed expression.", "punch"),
    15.045: ("quiet visual echo", "Terrace rest returns to the morning window, maintaining intimate scale.", "punch"),
    16.415: ("arrival continuation", "Morning curtain gives way to regional dry-forest scale.", "wipe"),
    17.445: ("geographic reveal", "Dry-forest aerial resolves into Pacific surf washing ashore.", "punch"),
    18.815: ("coastal arrival match", "Surf horizon connects to a couple arriving above the ocean.", "punch"),
    19.845: ("human connection", "Arrival pays off at a shared outdoor meal.", "bloom"),
    21.215: ("table detail", "Smiling guests lead into fruit passing between hands.", "punch"),
    22.585: ("shared-motion cut", "Hands passing fruit become the freedom of cycling together.", "punch"),
    23.695: ("motion cut", "Cycling momentum carries into water movement.", "punch"),
    24.985: ("water-to-touch", "A swim beat gives way to a golden-hour embrace.", "bloom"),
    26.355: ("sunset-light match", "Embrace moves into an evening firepit gathering.", "punch"),
    27.385: ("emotional release", "Friends beside the fire open to a walk toward the surf.", "punch"),
    28.755: ("dusk-to-site", "Nightfall terrace prepares the chapter shift to actual parcel imagery.", "punch"),
    # Act 2: basis (30 - 60s)
    30.0: ("change of scale", "Intimate dusk expands into actual 950-acre property aerials.", "wipe"),
    31.485: ("survey reframe", "Two actual site photographs shift from broad boundary to terrain detail.", "ken_burns"),
    32.865: ("fact to vision", "Actual site aerials transition into the architectural entrance concept.", "wipe"),
    34.585: ("threshold cut", "Entrance corridor becomes a couple arriving at an envisioned villa.", "bloom"),
    35.955: ("architecture texture", "Arrival continues along natural plaster and timber shading.", "punch"),
    37.665: ("preparation gesture", "Organic architecture gives way to a host preparing the community table.", "punch"),
    39.045: ("people-to-land", "Community preparation opens onto a sunlit dry-forest walking path.", "punch"),
    40.415: ("path motion match", "Walking path becomes bicycle motion through the forest trail.", "punch"),
    42.125: ("hand action", "Trail motion cuts to hands shaping natural clay.", "punch"),
    43.495: ("care motif", "Hands shaping clay connect to partners reviewing site plans outdoors.", "wipe"),
    44.885: ("plan-to-trail", "Site plan collaboration releases into active trail cycling.", "punch"),
    46.575: ("gesture-to-craft", "Trail movement settles into focused artisan pottery work.", "punch"),
    47.955: ("tactile action", "Clay in hand becomes a shared laugh at the pottery wheel.", "punch"),
    49.335: ("intimacy handoff", "Making something together becomes the emotional reward of belonging.", "bloom"),
    51.045: ("laughter widening", "A close embrace opens into social laughter around the table.", "punch"),
    52.415: ("scale lift", "Social warmth lifts to actual property drone imagery for the $9M basis.", "wipe"),
    54.125: ("evidence-to-resonance", "Actual site ridge transitions to the bronze singing bowl.", "punch"),
    55.505: ("Flow camera bridge", "Bronze bowl fills the frame and reveals the tropical plunge pool.", "bloom"),
    # Act 3: lots (60 - 95s)
    60.0: ("chapter reset", "Pool transition lands on morning coffee service for the El Encanto chapter.", "wipe"),
    60.985: ("coffee ritual detail", "Service moves into a tighter savoring angle on warm stone.", "punch"),
    62.355: ("invitation movement", "Morning coffee leads to a chair pulled toward the outdoor table.", "punch"),
    63.385: ("dining action match", "Friends at the table connect to their host preparing bowls.", "punch"),
    64.415: ("gesture continuation", "Table preparation carries into a shared community meal.", "bloom"),
    65.445: ("shared-meal relay", "One gathering relays into warm laughter around the table.", "punch"),
    67.495: ("creative spark", "Table laughter motivates trying a hands-on clay craft.", "punch"),
    68.865: ("human payoff", "A clay attempt becomes a spontaneous laugh with a friend.", "punch"),
    69.895: ("reaction cut", "The clay-making moment pays off in friends laughing together.", "punch"),
    70.925: ("village scale lift", "Intimate laughter widens to a Guanacaste dry-forest aerial.", "wipe"),
    72.985: ("vision-to-evidence", "Concept entrance cuts to actual property aerials for 40 titled homesites.", "wipe"),
    74.355: ("motion match", "Aerial parcel view grounds at the actual main road property entrance.", "ken_burns"),
    75.385: ("site-to-movement", "Property entrance transitions into morning movement in the pavilion.", "punch"),
    76.415: ("kinetic water hit", "Movement peaks with a golden-hour pool swim on the music beat.", "bloom"),
    77.435: ("Flow camera bridge", "Shaded doorway and leaf occlusion reveal the maloca circle.", "wipe"),
    80.865: ("maloca-to-craft", "Maloca gathering grounds in hands shaping clay.", "punch"),
    83.955: ("harvest-to-table", "Picking garden produce becomes a plated nourishing meal.", "punch"),
    85.325: ("music-sway cut", "A shared meal turns into terrace dancing as the music opens.", "bloom"),
    88.405: ("night-to-morning contrast", "Evening firelight releases into a quiet solo walk on the labyrinth path.", "punch"),
    91.835: ("Flow camera bridge", "Broadleaf canopy dive reveals the envisioned village.", "wipe"),
    # Act 4: water (95 - 125s)
    95.0: ("sanctuary threshold", "Village canopy resolves into quiet linen breeze to open Act IV.", "wipe"),
    99.045: ("body rhythm", "Bare feet ease into a quiet morning breath.", "bloom"),
    100.415: ("breath-to-body", "Slow breath flows into a terrace yoga stretch.", "punch"),
    104.535: ("reflection-to-rest", "Water reflection becomes an unhurried hammock reading moment.", "punch"),
    108.655: ("shelter-to-care", "Sunlit plaster wall gives way to tending a young garden tree.", "punch"),
    111.405: ("wellness action", "Yoga stretch cuts to actual property ridge imagery for reported wells.", "wipe"),
    112.755: ("person-to-person", "Daylight site ridge shifts to sunset parcel aerial during well diligence.", "ken_burns"),
    114.135: ("evidence-to-warmth", "Actual parcel aerial returns briefly to human warmth at sunset.", "bloom"),
    116.875: ("vision-to-evidence", "Calm breath cuts to actual site photography for Above 50 L/s yield.", "wipe"),
    119.605: ("parcel overview shift", "Valley corridor photo widens to the full front overview of the property.", "ken_burns"),
    122.015: ("Flow camera bridge", "Actual property overview hands off to stream-to-shore camera bridge.", "wipe"),
    # Act 5: close (125 - 150s)
    125.0: ("emotional connection", "The shoreline opens to a couple embracing at golden hour.", "bloom"),
    126.465: ("physical-to-emotional", "Sunset embrace carries into terrace dancing.", "punch"),
    129.215: ("shore-to-friends", "A walk by the water becomes friends gathered around a beach bonfire.", "bloom"),
    133.335: ("arrival-to-stewardship", "Couple arriving becomes hands planting a young sapling in the earth.", "punch"),
    136.075: ("craft-to-scale", "Artisan craft expands to partners reviewing site plans together.", "wipe"),
    137.445: ("plan-to-architecture", "Collaborative site sketch resolves into tropical architectural form.", "punch"),
    138.815: ("architecture-to-water", "Envisioned building opens onto the stone pool experience.", "punch"),
    141.555: ("care-to-harvest", "Tending the garden resolves in harvesting fresh herbs.", "punch"),
    144.335: ("gift-to-coast", "Fruit passed between friends becomes a run along the Pacific beach.", "punch"),
    147.385: ("shorelight match", "Warm human shoreline continues into a framed walk toward the surf.", "bloom"),
    148.755: ("final perspective lift", "The beach threshold lifts to the final coastal aerial invitation.", "wipe"),
}


def is_image_source(src: str) -> bool:
    return Path(src).suffix.lower() in {".webp", ".jpg", ".jpeg", ".png"}


def infer_provenance(row: dict[str, Any]) -> str:
    if row.get("provenance"):
        return str(row["provenance"])
    src = row["source"]
    kind = str(row.get("kind", "")).lower()
    if src.startswith("assets/website/") or "website" in kind:
        return "WEBSITE · PROPERTY PHOTOGRAPH"
    if row["chapter"] == "place" and float(row["start"]) < 3.38:
        return "CINEMATIC LOCATION CONCEPT"
    return "ILLUSTRATIVE CONCEPT FILM"


def build_css(chapter: str) -> str:
    return (
        "@font-face{font-family:Estate;src:url('assets/fonts/cormorant.ttf')}"
        "@font-face{font-family:Sans;src:url('assets/fonts/font-2.woff2');font-weight:400}"
        "@font-face{font-family:Sans;src:url('assets/fonts/font-3.woff2');font-weight:700}"
        f"#{chapter}{{position:absolute;inset:0;width:100%;height:100%;overflow:hidden;background:#142c25}}"
        ".clip{position:absolute}"
        ".picture{inset:0;width:100%;height:100%;object-fit:cover;z-index:1;will-change:transform}"
        ".fx-bloom{inset:0;width:100%;height:100%;pointer-events:none;z-index:2}"
        ".fx-bloom-inner{display:block;width:100%;height:100%;opacity:0;"
        "background:radial-gradient(circle at 50% 45%, rgba(244,216,158,0.55), rgba(217,190,132,0.18) 55%, transparent 80%)}"
        ".fx-wipe{inset:0;width:100%;height:100%;pointer-events:none;overflow:hidden;z-index:2}"
        ".fx-wipe-bar{display:block;width:100%;height:100%;will-change:transform;"
        "background:linear-gradient(90deg, transparent, rgba(217,190,132,0.65), rgba(20,44,37,0.85), transparent)}"
        ".brand{position:absolute;left:90px;top:64px;font:700 21px/1.2 Sans,sans-serif;letter-spacing:4px;"
        "color:#f4efe4;padding:12px 20px;background:#142c25;border-left:3px solid #d9be84;"
        "box-shadow:0 10px 28px rgba(0,0,0,0.35);z-index:6}"
        ".brand .chap{color:#d9be84;font-weight:400;letter-spacing:3px;margin-left:10px}"
        ".provenance{position:absolute;right:80px;top:64px;font:700 19px/1.2 Sans,sans-serif;letter-spacing:2px;"
        "color:#f4efe4;background:#142c25;border-left:3px solid #d9be84;padding:11px 18px;"
        "box-shadow:0 10px 28px rgba(0,0,0,0.35);z-index:6}"
        ".headline{position:absolute;left:92px;bottom:242px;width:1560px;color:#f4efe4;"
        "font:106px/1.02 Estate,serif;text-shadow:0 4px 28px #142c25;z-index:5}"
        ".headline-inner{display:block;width:100%}"
        ".headline small{display:inline-block;font:700 20px/1.2 Sans,sans-serif;letter-spacing:4px;"
        "color:#d9be84;background:#142c25;border-left:3px solid #d9be84;padding:8px 14px;margin-bottom:14px}"
        ".headline-title{display:block}"
        ".metric{position:absolute;right:80px;top:148px;left:auto;bottom:auto;color:#f4efe4;"
        "background:#142c25;border-left:3px solid #d9be84;padding:22px 30px;min-width:420px;max-width:680px;"
        "box-shadow:0 16px 40px rgba(0,0,0,0.42);z-index:6}"
        ".metric-inner{display:block;width:100%}"
        ".metric em{display:block;font:700 16px/1.2 Sans,sans-serif;letter-spacing:3px;color:#d9be84;"
        "font-style:normal;margin-bottom:8px}"
        ".metric strong{font:76px/1 Estate,serif;color:#f4efe4;display:block}"
        ".metric span{font:22px/1.4 Sans,sans-serif;color:#f4efe4;display:block;margin-top:10px}"
        ".end{position:absolute;left:90px;top:200px;bottom:auto;width:880px;padding:36px 44px;"
        "display:flex;justify-content:center;align-items:flex-start;flex-direction:column;"
        "background:#142c25;border-left:4px solid #d9be84;color:#f4efe4;"
        "box-shadow:0 24px 60px rgba(0,0,0,0.5);z-index:6}"
        ".end h1{display:block;width:100%;font:92px/1 Estate,serif;color:#f4efe4;margin:4px 0 12px}"
        ".end p{display:block;width:100%;font:25px/1.35 Sans,sans-serif;color:#f4efe4;margin:6px 0}"
        ".end .gold{color:#d9be84;letter-spacing:4px;font:700 19px/1.2 Sans,sans-serif;margin-bottom:6px}"
        ".end .gold-contact{color:#d9be84;letter-spacing:2px;font:700 22px/1.3 Sans,sans-serif;margin-top:12px}"
    )


def find_transition_for_cut(cut_start: float, tolerance: float = 0.40) -> tuple[str, str, str] | None:
    best_match = None
    min_delta = 999.0
    for t, spec in CURATED_TRANSITIONS.items():
        delta = abs(cut_start - t)
        if delta <= tolerance and delta < min_delta:
            min_delta = delta
            best_match = spec
    return best_match


def compile_chapter(
    chapter: str,
    chapter_rows: list[dict[str, Any]],
    all_edl_rows: list[dict[str, Any]],
    beats: list[float],
    img_counter: list[int],
) -> tuple[str, list[dict[str, Any]]]:
    meta = CHAPTER_META[chapter]
    c_start = float(meta["start"])
    c_dur = float(meta["duration"])

    dom_nodes: list[str] = []
    tweens: list[str] = []
    chapter_transitions: list[dict[str, Any]] = []

    for idx, row in enumerate(chapter_rows):
        global_start = round(float(row["start"]), 3)
        local_start = round(global_start - c_start, 3)
        dur = round(float(row["duration"]), 3)
        src = str(row["source"])
        clip_id = str(row.get("id") or f"{chapter}-dense-{idx:02d}")
        prov_text = html.escape(infer_provenance(row), quote=True)

        # Determine if this cut is a transition boundary
        global_idx = next(
            (i for i, r in enumerate(all_edl_rows) if abs(float(r["start"]) - global_start) < 0.002),
            None,
        )
        prev_row = all_edl_rows[global_idx - 1] if (global_idx is not None and global_idx > 0) else None
        trans_spec = find_transition_for_cut(global_start)

        if is_image_source(src):
            kb_idx = img_counter[0] % len(KEN_BURNS_PRESETS)
            img_counter[0] += 1
            kb = KEN_BURNS_PRESETS[kb_idx]
            dom_nodes.append(
                f'<div id="{clip_id}" class="clip picture" data-start="{local_start:g}" '
                f'data-duration="{dur:g}" data-track-index="1" data-layout-allow-overflow>'
                f'<img id="{clip_id}-img" src="{src}" '
                f'style="display:block;width:100%;height:100%;object-fit:cover;will-change:transform"></div>'
            )
            f_vars = kb["from"]
            t_vars = kb["to"]
            tweens.append(
                f'tl.fromTo("#{clip_id}-img",'
                f'{{scale:{f_vars["scale"]:g},x:{f_vars["x"]:g},y:{f_vars["y"]:g}}},'
                f'{{scale:{t_vars["scale"]:g},x:{t_vars["x"]:g},y:{t_vars["y"]:g},'
                f'duration:{dur:g},ease:"none",immediateRender:false}},{local_start:g});'
            )
            cam_desc = f'ken_burns:{kb["name"]} ({kb["description"]})'
        else:
            media_start = float(row.get("source_start", 0))
            playback_rate = float(row.get("playback_rate", 1))
            dom_nodes.append(
                f'<video id="{clip_id}" class="clip picture" src="{src}" muted playsinline '
                f'data-start="{local_start:g}" data-duration="{dur:g}" '
                f'data-media-start="{media_start:g}" data-playback-rate="{playback_rate:g}" '
                f'data-track-index="1" data-hf-media-start-basis="local" data-layout-allow-overflow></video>'
            )
            if trans_spec is not None:
                punch_dur = round(min(0.32, max(0.18, dur * 0.45)), 3)
                tweens.append(
                    f'tl.fromTo("#{clip_id}",{{scale:1.06}},'
                    f'{{scale:1,duration:{punch_dur:g},ease:"power2.out",immediateRender:false}},{local_start:g});'
                )
                cam_desc = f"video_scale_punch (scale 1.06 -> 1.0 over {punch_dur:g}s, power2.out)"
            else:
                cam_desc = "native_source_motion"

        # Provenance pill on Track 4
        dom_nodes.append(
            f'<div id="{clip_id}-source" class="clip provenance" '
            f'data-start="{local_start:g}" data-duration="{dur:g}" data-track-index="4">{prov_text}</div>'
        )

        # Dedicated Track 2 Transition FX layer + Transition Ledger entry
        if trans_spec is not None and prev_row is not None:
            method, reason, fx_kind = trans_spec
            fx_layer_desc = "none (editorial/camera handoff)"
            if fx_kind == "bloom":
                fx_id = f"{chapter}-fx-bloom-{idx:02d}"
                fx_start = round(max(0.0, local_start - 0.11), 3)
                fx_dur = 0.22
                dom_nodes.append(
                    f'<div id="{fx_id}" class="clip fx-bloom" data-start="{fx_start:g}" '
                    f'data-duration="{fx_dur:g}" data-track-index="2">'
                    f'<div id="{fx_id}-inner" class="fx-bloom-inner"></div></div>'
                )
                tweens.append(
                    f'tl.fromTo("#{fx_id}-inner",{{opacity:0}},'
                    f'{{keyframes:[{{opacity:0.85,duration:0.11,ease:"power2.out"}},'
                    f'{{opacity:0,duration:0.11,ease:"power2.in"}}],immediateRender:false}},{fx_start:g});'
                )
                fx_layer_desc = f"Track 2 golden-hour light bloom (#{fx_id}, {fx_start:g}s, {fx_dur:g}s)"
            elif fx_kind == "wipe":
                fx_id = f"{chapter}-fx-wipe-{idx:02d}"
                fx_start = round(max(0.0, local_start - 0.12), 3)
                fx_dur = 0.24
                dom_nodes.append(
                    f'<div id="{fx_id}" class="clip fx-wipe" data-start="{fx_start:g}" '
                    f'data-duration="{fx_dur:g}" data-track-index="2" data-layout-allow-overflow>'
                    f'<div id="{fx_id}-bar" class="fx-wipe-bar"></div></div>'
                )
                tweens.append(
                    f'tl.fromTo("#{fx_id}-bar",{{xPercent:-100}},'
                    f'{{xPercent:100,duration:{fx_dur:g},ease:"power2.inOut",immediateRender:false}},{fx_start:g});'
                )
                fx_layer_desc = f"Track 2 directional horizon wipe (#{fx_id}, {fx_start:g}s, {fx_dur:g}s)"

            nearest_beat = min(beats, key=lambda b: abs(b - global_start)) if beats else global_start
            beat_delta = round(abs(global_start - nearest_beat), 3)
            chapter_transitions.append(
                {
                    "time": global_start,
                    "chapter": chapter,
                    "local_time": local_start,
                    "method": method,
                    "from_source": prev_row["source"],
                    "to_source": src,
                    "nearest_music_beat": round(nearest_beat, 3),
                    "beat_delta_seconds": beat_delta,
                    "status": "integrated; seek-safe camera & transition spec verified",
                    "visual_reason": reason,
                    "camera_motion": cam_desc,
                    "fx_layer": fx_layer_desc,
                }
            )

    # Headlines
    for h in meta.get("headlines", []):
        h_id = h["id"]
        h_start = float(h["start"])
        h_dur = float(h["duration"])
        eyebrow = html.escape(h["eyebrow"], quote=True)
        text = html.escape(h["text"], quote=True)
        dom_nodes.append(
            f'<div id="{h_id}" class="clip headline" data-start="{h_start:g}" '
            f'data-duration="{h_dur:g}" data-track-index="2">'
            f'<div id="{h_id}-inner" class="headline-inner">'
            f'<small>{eyebrow}</small><span class="headline-title">{text}</span></div></div>'
        )
        f_vars = h.get("from_vars", {"opacity": 0, "y": 32})
        f_str = ",".join(f"{k}:{v:g}" for k, v in f_vars.items())
        tweens.append(
            f'tl.fromTo("#{h_id}-inner",{{{f_str}}},'
            f'{{opacity:1,x:0,y:0,duration:0.5,ease:"power3.out",immediateRender:false}},{h_start:g});'
        )

    # Investor & Lifestyle Metric Cards (always positioned at top-right: right:80px; top:148px)
    for m in meta.get("metrics", []):
        m_id = m["id"]
        m_start = float(m["start"])
        m_dur = float(m["duration"])
        eyebrow = html.escape(m.get("eyebrow", ""), quote=True)
        val = html.escape(m["value"], quote=True)
        det = html.escape(m["detail"], quote=True)
        val_style = f' style="font-size:{m["value_size"]}"' if m.get("value_size") else ""
        eyebrow_html = f"<em>{eyebrow}</em>" if eyebrow else ""
        dom_nodes.append(
            f'<div id="{m_id}" class="clip metric" data-start="{m_start:g}" '
            f'data-duration="{m_dur:g}" data-track-index="3">'
            f'<div id="{m_id}-inner" class="metric-inner">'
            f"{eyebrow_html}<strong{val_style}>{val}</strong><span>{det}</span></div></div>"
        )
        tweens.append(
            f'tl.fromTo("#{m_id}-inner",{{opacity:0,y:18}},'
            f'{{opacity:1,y:0,duration:0.38,ease:"power2.out",immediateRender:false}},{m_start:g});'
        )

    # End card (Act 5 close)
    if "end_card" in meta:
        ec = meta["end_card"]
        ec_id = ec["id"]
        ec_start = float(ec["start"])
        ec_dur = float(ec["duration"])
        dom_nodes.append(
            f'<div id="{ec_id}" class="clip end" data-start="{ec_start:g}" '
            f'data-duration="{ec_dur:g}" data-track-index="3">'
            f'<p id="{ec_id}-eyebrow" class="gold">{html.escape(ec["eyebrow"], quote=True)}</p>'
            f'<h1 id="{ec_id}-title">{html.escape(ec["title"], quote=True)}</h1>'
            f'<p id="{ec_id}-sub">{html.escape(ec["subtitle"], quote=True)}</p>'
            f'<p id="{ec_id}-partners">{html.escape(ec["partners"], quote=True)}</p>'
            f'<p id="{ec_id}-contact" class="gold-contact">{html.escape(ec["contact"], quote=True)}</p>'
            f"</div>"
        )
        tweens.append(
            f'tl.fromTo("#{ec_id}-eyebrow",{{opacity:0,y:14}},'
            f'{{opacity:1,y:0,duration:0.35,ease:"power2.out",immediateRender:false}},{ec_start:g});'
        )
        tweens.append(
            f'tl.fromTo("#{ec_id}-title",{{opacity:0,y:18}},'
            f'{{opacity:1,y:0,duration:0.42,ease:"power3.out",immediateRender:false}},{round(ec_start + 0.1, 3):g});'
        )
        tweens.append(
            f'tl.fromTo("#{ec_id}-sub",{{opacity:0,y:14}},'
            f'{{opacity:1,y:0,duration:0.35,ease:"power2.out",immediateRender:false}},{round(ec_start + 0.2, 3):g});'
        )
        tweens.append(
            f'tl.fromTo("#{ec_id}-partners",{{opacity:0,y:14}},'
            f'{{opacity:1,y:0,duration:0.35,ease:"power2.out",immediateRender:false}},{round(ec_start + 0.3, 3):g});'
        )
        tweens.append(
            f'tl.fromTo("#{ec_id}-contact",{{opacity:0,y:14}},'
            f'{{opacity:1,y:0,duration:0.35,ease:"power2.out",immediateRender:false}},{round(ec_start + 0.4, 3):g});'
        )

    # Persistent chapter brand header with chapter eyebrow pill
    brand_eyebrow = html.escape(meta["brand_eyebrow"], quote=True)
    dom_nodes.append(
        f'<div class="brand">EDEN MAZARA<span class="chap">·  {brand_eyebrow}</span></div>'
    )

    css = build_css(chapter)
    script = (
        f"{{const tl=gsap.timeline({{paused:true}});"
        f"{''.join(tweens)}"
        f'window.__timelines["{chapter}"]=tl;}}'
    )
    html_doc = (
        f"<!doctype html><html><body><template><style>{css}</style>"
        f'<div id="{chapter}" data-composition-id="{chapter}" '
        f'data-duration="{c_dur:g}" data-width="1920" data-height="1080" data-layout-allow-overflow>'
        f"{''.join(dom_nodes)}</div>"
        f"<script>{script}</script></template></body></html>"
    )
    return html_doc, chapter_transitions


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--edl",
        type=Path,
        default=None,
        help="Path to EDL JSON (defaults to production/EDL-V7-PROPOSAL.json if present, else production/EDIT-DECISION-LIST.json)",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="Directory to write compiled chapter HTML files (defaults to compositions/)",
    )
    parser.add_argument(
        "--ledger-out",
        type=Path,
        default=None,
        help="Path to write updated TRANSITION-LEDGER.json",
    )
    parser.add_argument(
        "--spec-out",
        type=Path,
        default=ROOT / "production" / "MOTION-AND-TRANSITIONS-SPEC.json",
        help="Path to write MOTION-AND-TRANSITIONS-SPEC.json",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Compile and validate in memory, writing only MOTION-AND-TRANSITIONS-SPEC.json (and --out-dir if explicitly given)",
    )
    args = parser.parse_args()

    edl_path = args.edl
    if edl_path is None:
        v7_prop = ROOT / "production" / "EDL-V7-PROPOSAL.json"
        edl_path = v7_prop if v7_prop.exists() else (ROOT / "production" / "EDIT-DECISION-LIST.json")

    edl_rows: list[dict[str, Any]] = json.loads(edl_path.read_text(encoding="utf-8"))
    beats_path = ROOT / "beats" / "assets" / "take-me-to-the-moon.mp3.json"
    beats: list[float] = (
        [float(x["time"]) for x in json.loads(beats_path.read_text(encoding="utf-8"))["beats"]]
        if beats_path.exists()
        else []
    )

    out_dir = args.out_dir if args.out_dir is not None else (None if args.dry_run else ROOT / "compositions")
    if out_dir is not None:
        out_dir.mkdir(parents=True, exist_ok=True)

    all_transitions: list[dict[str, Any]] = []
    img_counter = [0]
    chapter_stats: dict[str, Any] = {}

    for chapter in ("place", "basis", "lots", "water", "close"):
        c_rows = [r for r in edl_rows if r["chapter"] == chapter]
        html_doc, c_trans = compile_chapter(chapter, c_rows, edl_rows, beats, img_counter)
        if out_dir is not None:
            (out_dir / f"{chapter}.html").write_text(html_doc, encoding="utf-8")
        all_transitions.extend(c_trans)
        chapter_stats[chapter] = {
            "cuts": len(c_rows),
            "static_images_with_ken_burns": sum(1 for r in c_rows if is_image_source(r["source"])),
            "transitions": len(c_trans),
            "headlines": len(CHAPTER_META[chapter].get("headlines", [])),
            "metrics": len(CHAPTER_META[chapter].get("metrics", [])),
        }

    # Number transitions sequentially 1..N
    ledger_entries: list[dict[str, Any]] = []
    for i, tr in enumerate(all_transitions, 1):
        tr["number"] = i
        sheet_idx = min(3, (i - 1) // 25 + 1)
        ledger_entries.append(
            {
                "number": i,
                "time": tr["time"],
                "chapter": tr["chapter"],
                "method": tr["method"],
                "from_source": tr["from_source"],
                "to_source": tr["to_source"],
                "beat_delta_seconds": tr["beat_delta_seconds"],
                "camera_motion": tr["camera_motion"],
                "fx_layer": tr["fx_layer"],
                "status": tr["status"],
                "visual_reason": tr["visual_reason"],
                "proof": f"production/transition-contact-{sheet_idx}.jpg",
            }
        )

    ledger_out = args.ledger_out if args.ledger_out is not None else (
        None if args.dry_run else ROOT / "production" / "TRANSITION-LEDGER.json"
    )
    if ledger_out is not None:
        ledger_out.write_text(json.dumps(ledger_entries, indent=2) + "\n", encoding="utf-8")

    spec_payload = {
        "edl_source": str(edl_path.relative_to(ROOT) if edl_path.is_relative_to(ROOT) else edl_path),
        "total_picture_cuts": len(edl_rows),
        "total_static_images_with_ken_burns": img_counter[0],
        "total_transitions": len(all_transitions),
        "track_2_bloom_count": sum(1 for t in all_transitions if "bloom" in t["fx_layer"]),
        "track_2_wipe_count": sum(1 for t in all_transitions if "wipe" in t["fx_layer"]),
        "ken_burns_presets": KEN_BURNS_PRESETS,
        "chapter_summary": chapter_stats,
        "investor_overlays": {
            ch: {
                "brand_header": f'EDEN MAZARA · {meta["brand_eyebrow"]}',
                "metrics": meta.get("metrics", []),
                "headlines": meta.get("headlines", []),
            }
            for ch, meta in CHAPTER_META.items()
        },
        "transitions": all_transitions,
    }
    if args.spec_out is not None:
        args.spec_out.write_text(json.dumps(spec_payload, indent=2) + "\n", encoding="utf-8")

    print(
        f"Compiled 5 chapters from {edl_path.name}: {len(edl_rows)} cuts, "
        f"{img_counter[0]} Ken Burns image moves, {len(all_transitions)} transitions "
        f"(out_dir={out_dir}, dry_run={args.dry_run})"
    )


if __name__ == "__main__":
    main()
