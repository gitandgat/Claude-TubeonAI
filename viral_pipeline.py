#!/usr/bin/env python3
"""
Crosswalk Wisdom — Viral Intelligence Pipeline
================================================
Stage 1  Apify crosswalk-viral-scout  → top competitor Reels
Stage 2  Gemini 2.0 Flash             → analyze each video (Hook / Concept / Script)
Stage 3  Claude Sonnet                → adapt best concept into CW script
Stage 4  HeyGen                       → talking-head .mp4 from script
Stage 5  Remotion (video-edit)        → captions + overlays + music
Stage 6  Zernio                       → schedule to 5 platforms

Usage:
    python viral_pipeline.py                        # full run
    python viral_pipeline.py --stage intel          # only Stage 1
    python viral_pipeline.py --stage script         # only Stage 3 (needs intel output)
    python viral_pipeline.py --stage heygen         # only Stage 4 (needs script output)
    python viral_pipeline.py --handles dr.x,md.y   # override competitor handles
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
import urllib.error
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# ── Config ────────────────────────────────────────────────────────────────────

APIFY_TOKEN     = os.getenv("APIFY_API_TOKEN", "")
GEMINI_KEY      = os.getenv("GEMINI_API_KEY", "")
ANTHROPIC_KEY   = os.getenv("ANTHROPIC_API_KEY", "")
HEYGEN_KEY      = os.getenv("HEYGEN_API_KEY", "")
HEYGEN_AVATAR   = os.getenv("HEYGEN_AVATAR_ID", "")   # Sahawat's self-clone avatar ID
HEYGEN_VOICE    = os.getenv("HEYGEN_VOICE_ID", "")    # Sahawat's cloned voice ID

# Local $0 talking-head engine (SadTalker + VoiSpark) — default Stage-4 backend.
# Runs under its own conda env (torch 2.0.1); invoked as a subprocess.
# resolve() so paths are absolute regardless of how the script is invoked.
REPO_DIR     = Path(__file__).resolve().parent
AVATAR_PY    = "/opt/anaconda3/envs/avatar/bin/python"
AVATAR_DIR   = REPO_DIR / "avatar-engine"
AVATAR_HOOK  = AVATAR_DIR / "avatar_hook.py"
AVATAR_FACE  = AVATAR_DIR / "faces" / "sahawat.jpg"

# Battle-tested marketplace scraper — called directly so all ranking logic stays
# local and debuggable (replaces the hand-rolled crosswalk-viral-scout actor).
INSTAGRAM_SCRAPER = "apify~instagram-scraper"

# Default competitor handles — burnout / career-pivot coaches for physicians.
# Verified live against Apify (2026-06-22); all post video reels in-niche.
# ejones_md hit 15.2M views on a single reel — strongest viral signal.
DEFAULT_HANDLES = [
    "ejones_md",          # burnout → clarity coach for healthcare pros
    "shani_esparazmd",    # burnout / wellness coach, women in healthcare
    "bounceupcoaching",   # physician career coach (direct competitor)
]

OUT_DIR = REPO_DIR / "pipeline-output"
OUT_DIR.mkdir(exist_ok=True)

GEMINI_MODEL        = "gemini-2.5-flash"  # 2.0-flash has limit:0 on free tier; 2.5-flash has quota + video support
GEMINI_UPLOAD_URL   = "https://generativelanguage.googleapis.com/upload/v1beta/files"
GEMINI_GENERATE_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
HEYGEN_GENERATE_URL = "https://api.heygen.com/v2/video/generate"
HEYGEN_STATUS_URL   = "https://api.heygen.com/v1/video_status.get"
APIFY_RUN_URL       = f"https://api.apify.com/v2/acts/{INSTAGRAM_SCRAPER}/run-sync-get-dataset-items"

# ── Helpers ───────────────────────────────────────────────────────────────────

def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def _apify_post(path: str, body: dict) -> dict:
    url = f"https://api.apify.com/v2{path}?token={APIFY_TOKEN}"
    data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.loads(r.read())


def _http_post(url: str, body: dict, headers: dict | None = None) -> dict:
    data = json.dumps(body).encode()
    h = {"Content-Type": "application/json", **(headers or {})}
    req = urllib.request.Request(url, data=data, headers=h)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


def _http_get(url: str, headers: dict | None = None) -> dict:
    req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


# ── Stage 1: Intel (Apify) ────────────────────────────────────────────────────

def run_intel(handles: list[str], n_days: int = 30, top_k: int = 10) -> list[dict]:
    log(f"Stage 1 — Scraping {len(handles)} accounts via apify~instagram-scraper…")
    if not APIFY_TOKEN:
        sys.exit("ERROR: APIFY_API_TOKEN not set in .env")

    handles = [h.strip().lstrip("@") for h in handles if h.strip()]
    cutoff = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=n_days)
    cutoff_str = cutoff.date().isoformat()

    body = {
        "directUrls": [f"https://www.instagram.com/{h}/" for h in handles],
        "resultsType": "posts",
        "resultsLimit": 20,                 # recent posts per account
        "onlyPostsNewerThan": cutoff_str,
        "addParentData": False,
    }
    url = f"{APIFY_RUN_URL}?token={APIFY_TOKEN}"
    req = urllib.request.Request(
        url, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"}
    )

    log(f"  Running scraper for {len(handles)} accounts (this may take 1-4 min)…")
    try:
        with urllib.request.urlopen(req, timeout=600) as r:
            items = json.loads(r.read())
    except urllib.error.HTTPError as e:
        sys.exit(f"Apify scrape failed (HTTP {e.code}): {e.read().decode()[:500]}")

    log(f"  → {len(items)} raw posts scraped — filtering to video reels…")

    reels = []
    for item in items:
        if not item.get("videoUrl"):
            continue
        ts = item.get("timestamp")
        if not ts:
            continue
        try:
            posted = datetime.datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except ValueError:
            continue
        if posted < cutoff:
            continue
        short = item.get("shortCode")
        reels.append({
            "handle":    item.get("ownerUsername") or "",
            "videoUrl":  item["videoUrl"],
            "postUrl":   item.get("url") or (f"https://www.instagram.com/reel/{short}/" if short else ""),
            "views":     item.get("videoPlayCount") or item.get("videoViewCount") or 0,
            "likes":     item.get("likesCount") or 0,
            "comments":  item.get("commentsCount") or 0,
            "thumbnail": (item.get("images") or [None])[0] or item.get("displayUrl") or "",
            "caption":   (item.get("caption") or "")[:300],
            "timestamp": ts,
            "scrapedAt": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        })

    ranked = sorted(reels, key=lambda r: r["views"], reverse=True)[:top_k]
    log(f"  → {len(reels)} video reels in window, returning top {len(ranked)} by views")
    for i, r in enumerate(ranked, 1):
        log(f"    {i}. @{r['handle']} — {r['views']:,} views")

    out = OUT_DIR / "intel.json"
    out.write_text(json.dumps(ranked, indent=2))
    log(f"  Saved → {out}")
    return ranked


# ── Stage 2: Analyze (Gemini) ─────────────────────────────────────────────────

GEMINI_ANALYSIS_PROMPT = """You are analyzing a viral Instagram Reel from a doctor/health coach.
Extract the following in JSON:
{
  "hook": "the exact opening line or visual that stops the scroll (1-2 sentences)",
  "concept": "the core idea or insight being delivered (1 sentence)",
  "retention": "what keeps viewers watching past 3 seconds (mechanism)",
  "format": "the content format (talking-head / B-roll / text-over / interview / etc.)",
  "script_skeleton": "the rough narrative arc in 3-4 bullet points",
  "why_viral": "the single most important reason this got high views"
}
Return ONLY valid JSON, no markdown."""


def analyze_one(video_url: str, handle: str) -> dict | None:
    if not GEMINI_KEY:
        log("  SKIP: GEMINI_API_KEY not set")
        return None

    # Download video to temp file
    try:
        log(f"  Downloading video from @{handle}…")
        with urllib.request.urlopen(video_url, timeout=30) as r:
            video_bytes = r.read()
    except Exception as e:
        log(f"  Download failed: {e}")
        return None

    # Upload to Gemini Files API
    try:
        log("  Uploading to Gemini…")
        upload_req = urllib.request.Request(
            f"{GEMINI_UPLOAD_URL}?key={GEMINI_KEY}",
            data=video_bytes,
            headers={
                "X-Goog-Upload-Command": "start, upload, finalize",
                "X-Goog-Upload-Header-Content-Length": str(len(video_bytes)),
                "X-Goog-Upload-Header-Content-Type": "video/mp4",
                "Content-Type": "video/mp4",
            },
        )
        with urllib.request.urlopen(upload_req, timeout=120) as r:
            upload_data = json.loads(r.read())
        file_uri = upload_data["file"]["uri"]
        file_name = upload_data["file"]["name"]
        mime_type = upload_data["file"]["mimeType"]
    except Exception as e:
        log(f"  Upload failed: {e}")
        return None

    # Wait for ACTIVE state
    for _ in range(30):
        time.sleep(4)
        try:
            status_req = urllib.request.Request(
                f"https://generativelanguage.googleapis.com/v1beta/{file_name}?key={GEMINI_KEY}"
            )
            with urllib.request.urlopen(status_req, timeout=30) as r:
                s = json.loads(r.read())
            if s.get("state") == "ACTIVE":
                break
            if s.get("state") == "FAILED":
                log("  Gemini file processing failed")
                return None
        except Exception:
            pass

    # Analyze (with one backoff retry on 429 — free tier is per-minute limited)
    body = {
        "contents": [{
            "role": "user",
            "parts": [
                {"fileData": {"fileUri": file_uri, "mimeType": mime_type}},
                {"text": GEMINI_ANALYSIS_PROMPT},
            ],
        }]
    }
    for attempt in range(2):
        try:
            analyze_req = urllib.request.Request(
                f"{GEMINI_GENERATE_URL}?key={GEMINI_KEY}",
                data=json.dumps(body).encode(),
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(analyze_req, timeout=60) as r:
                result = json.loads(r.read())
            raw = result["candidates"][0]["content"]["parts"][0]["text"]
            raw = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
            return json.loads(raw)
        except urllib.error.HTTPError as e:
            detail = e.read().decode()[:300]
            if e.code == 429 and attempt == 0:
                log("  Rate-limited (429) — waiting 45s then retrying once…")
                time.sleep(45)
                continue
            log(f"  Analysis failed: HTTP {e.code} — {detail}")
            return None
        except Exception as e:
            log(f"  Analysis failed: {e}")
            return None


def run_analysis(reels: list[dict], max_analyze: int = 5) -> list[dict]:
    log(f"Stage 2 — Analyzing top {max_analyze} reels with Gemini…")
    analyzed = []
    for reel in reels[:max_analyze]:
        log(f"  @{reel['handle']} — {reel['views']:,} views")
        analysis = analyze_one(reel["videoUrl"], reel["handle"])
        if analysis:
            analyzed.append({**reel, "analysis": analysis})
            log(f"    Hook: {analysis.get('hook', '')[:80]}…")

    out = OUT_DIR / "analyzed.json"
    out.write_text(json.dumps(analyzed, indent=2))
    log(f"  Saved → {out} ({len(analyzed)} analyzed)")
    return analyzed


# ── Stage 3: Generate Script (Claude) ────────────────────────────────────────

SCRIPT_PROMPT = """You are a content strategist for Crosswalk Wisdom, a brand by Sahawat Thongsai — a former physician
who coaches unmatched IMGs and burned-out doctors to build lives beyond medicine.

Brand voice: direct, no fluff, first-person, earned authority from real medical experience.
Tagline: "From the Ward to the World."
Audience: unmatched IMGs and burned-out physicians aged 28-42, stuck in identity/career transition.

Here are the top viral reference videos from competitor accounts this week:

{analyses}

Based on these viral patterns, generate ONE adapted talking-head script for Sahawat.
The script must:
- Open with a hook that stops the scroll in under 3 seconds (real story, not a question)
- Run 45-60 seconds at natural speaking pace (~130 words)
- Use Sahawat's "former physician" lens — not medical advice, but a career/identity perspective
- End with a soft CTA that points toward the Fear Audit or the IMG calculator
- Pass the anti-slop test: no "game-changer", "unlock", "skyrocket", "dive into", "journey"

Return JSON:
{{
  "title": "short internal title for this piece",
  "hook": "the exact opening line",
  "script": "full word-for-word script, 130-150 words",
  "caption": "Instagram/TikTok caption (120 chars max, no hashtags)",
  "hashtags": ["tag1", "tag2", "tag3", "tag4", "tag5"],
  "overlay_moments": [
    {{"at_word": "approximate word where overlay fires", "type": "callout|stat_punch|keyword_chips", "content": "overlay text"}}
  ],
  "cta_url": "https://www.crosswalkwisdom.com/img/calculator"
}}"""


def run_script_generation(analyzed: list[dict]) -> dict:
    log("Stage 3 — Generating script with Claude…")
    if not ANTHROPIC_KEY:
        sys.exit("ERROR: ANTHROPIC_API_KEY not set in .env")
    if not analyzed:
        sys.exit("ERROR: No analyzed reels to generate from")

    # Format analyses for the prompt
    summaries = []
    for i, item in enumerate(analyzed[:5], 1):
        a = item.get("analysis", {})
        summaries.append(
            f"Video {i} (@{item['handle']}, {item['views']:,} views)\n"
            f"  Hook: {a.get('hook', 'N/A')}\n"
            f"  Concept: {a.get('concept', 'N/A')}\n"
            f"  Why viral: {a.get('why_viral', 'N/A')}"
        )

    prompt = SCRIPT_PROMPT.format(analyses="\n\n".join(summaries))

    body = {
        "model": "claude-sonnet-4-6",
        "max_tokens": 2048,
        "messages": [{"role": "user", "content": prompt}],
    }
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps(body).encode(),
        headers={
            "Content-Type": "application/json",
            "x-api-key": ANTHROPIC_KEY,
            "anthropic-version": "2023-06-01",
        },
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        result = json.loads(r.read())

    raw = result["content"][0]["text"].strip().lstrip("```json").lstrip("```").rstrip("```").strip()
    script_data = json.loads(raw)

    out = OUT_DIR / "script.json"
    out.write_text(json.dumps(script_data, indent=2))
    log(f"  Title: {script_data.get('title')}")
    log(f"  Hook: {script_data.get('hook', '')[:80]}…")
    log(f"  Script: {len(script_data.get('script', '').split())} words")
    log(f"  Saved → {out}")
    return script_data


# ── Stage 4 (default): Local $0 Talking-Head (SadTalker + VoiSpark) ────────────

def _slug(script_data: dict) -> str:
    return script_data.get("title", "video").lower().replace(" ", "-")[:40]


def run_avatar_local(script_data: dict) -> Path:
    log("Stage 4 — Generating talking-head via local SadTalker+VoiSpark ($0)…")
    if not AVATAR_HOOK.exists():
        sys.exit(f"ERROR: avatar engine not found at {AVATAR_HOOK}")
    if not Path(AVATAR_PY).exists():
        sys.exit(f"ERROR: avatar conda env python missing at {AVATAR_PY}")
    if not AVATAR_FACE.exists():
        sys.exit(f"ERROR: no selfie at {AVATAR_FACE} — drop a front-facing photo there")

    slug = _slug(script_data)
    script_text = script_data["script"]
    log(f"  Script: {len(script_text.split())} words → VoiSpark voiceover → SadTalker (CPU, 256px)")
    log("  NOTE: CPU render of a ~60s clip is slow — this can take a while.")

    cmd = [
        AVATAR_PY, "-u",               # unbuffered so voiceover/render logs stream to the caller
        str(AVATAR_HOOK),
        slug,                          # custom slug (allowed because --text is passed)
        "--text", script_text,
        "--photo", str(AVATAR_FACE),
        "--render-only",               # reuse cached wav if this slug was rendered before
    ]
    # Run from the engine dir so SadTalker's relative paths resolve.
    proc = subprocess.run(cmd, cwd=str(AVATAR_DIR))
    if proc.returncode != 0:
        sys.exit(f"Local avatar render failed (exit {proc.returncode})")

    produced = AVATAR_DIR / "out" / f"{slug}-avatar-hook.mp4"
    if not produced.exists():
        sys.exit(f"Avatar engine reported success but no file at {produced}")

    out_path = OUT_DIR / f"{slug}-raw.mp4"
    shutil.copyfile(produced, out_path)
    log(f"  Done → {out_path} ({out_path.stat().st_size // 1024:,} KB)")
    return out_path


# ── Stage 4 (alt): HeyGen Talking-Head (needs paid API credits) ───────────────

def run_heygen(script_data: dict) -> Path:
    log("Stage 4 — Generating talking-head via HeyGen…")
    if not HEYGEN_KEY:
        sys.exit("ERROR: HEYGEN_API_KEY not set in .env")
    if not HEYGEN_AVATAR:
        sys.exit("ERROR: HEYGEN_AVATAR_ID not set in .env  (find it in HeyGen → Avatars)")
    if not HEYGEN_VOICE:
        sys.exit("ERROR: HEYGEN_VOICE_ID not set in .env  (find it in HeyGen → Voices)")

    script_text = script_data["script"]
    log(f"  Script: {len(script_text.split())} words")

    body = {
        "video_inputs": [{
            "character": {
                "type": "avatar",
                "avatar_id": HEYGEN_AVATAR,
                "avatar_style": "normal",
            },
            "voice": {
                "type": "text",
                "input_text": script_text,
                "voice_id": HEYGEN_VOICE,
                "speed": 1.0,
            },
            "background": {
                "type": "color",
                "value": "#1A1A1A",  # Crosswalk charcoal — replaces green-screen in post
            },
        }],
        "dimension": {"width": 1080, "height": 1920},  # 9:16 for TikTok/Reels
        "test": False,
    }

    req = urllib.request.Request(
        HEYGEN_GENERATE_URL,
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "X-Api-Key": HEYGEN_KEY},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        result = json.loads(r.read())

    video_id = result.get("data", {}).get("video_id")
    if not video_id:
        sys.exit(f"HeyGen error: {result}")
    log(f"  Video ID: {video_id}  — polling for completion…")

    # Poll until COMPLETED
    for attempt in range(60):
        time.sleep(15)
        status_req = urllib.request.Request(
            f"{HEYGEN_STATUS_URL}?video_id={video_id}",
            headers={"X-Api-Key": HEYGEN_KEY},
        )
        with urllib.request.urlopen(status_req, timeout=30) as r:
            status = json.loads(r.read())
        state = status.get("data", {}).get("status", "")
        log(f"  [{attempt+1}] {state}")
        if state == "completed":
            video_url = status["data"]["video_url"]
            break
        if state == "failed":
            sys.exit(f"HeyGen render failed: {status}")
    else:
        sys.exit("HeyGen timed out after 15 minutes")

    # Download the video
    out_path = OUT_DIR / f"{_slug(script_data)}-raw.mp4"
    log(f"  Downloading → {out_path}")
    urllib.request.urlretrieve(video_url, out_path)
    log(f"  Done ({out_path.stat().st_size // 1024:,} KB)")
    return out_path


# ── Stage 5: Remotion Edit (video-edit skill) ─────────────────────────────────

def run_edit(video_path: Path, script_data: dict) -> None:
    """Placeholder — the video-edit skill handles this step interactively.
    Run this from Claude Code: /video-edit  with the output video path.
    The overlay_moments from script.json seed the broll_plan.json automatically."""
    log("Stage 5 — Remotion edit")
    log(f"  Input: {video_path}")
    log("  → Hand to /video-edit skill in Claude Code with the script.json overlay_moments")
    log("  → OR run: cd crosswalk-remotion && npm start to preview")


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Crosswalk Viral Pipeline")
    parser.add_argument("--stage", choices=["intel", "analyze", "script", "avatar", "heygen", "all"],
                        default="all")
    parser.add_argument("--backend", choices=["local", "heygen"], default="local",
                        help="Stage-4 talking-head engine (default: local $0 SadTalker+VoiSpark)")
    parser.add_argument("--handles", help="Comma-separated Instagram handles to scrape")
    parser.add_argument("--days", type=int, default=30)
    parser.add_argument("--topk", type=int, default=10)
    args = parser.parse_args()

    handles = args.handles.split(",") if args.handles else DEFAULT_HANDLES

    if args.stage in ("intel", "all"):
        reels = run_intel(handles, n_days=args.days, top_k=args.topk)
    else:
        intel_file = OUT_DIR / "intel.json"
        if not intel_file.exists():
            sys.exit("Run --stage intel first")
        reels = json.loads(intel_file.read_text())

    if args.stage in ("analyze", "all"):
        analyzed = run_analysis(reels)
    else:
        analyzed_file = OUT_DIR / "analyzed.json"
        if not analyzed_file.exists():
            sys.exit("Run --stage analyze first")
        analyzed = json.loads(analyzed_file.read_text())

    if args.stage in ("script", "all"):
        script_data = run_script_generation(analyzed)
    else:
        script_file = OUT_DIR / "script.json"
        if not script_file.exists():
            sys.exit("Run --stage script first")
        script_data = json.loads(script_file.read_text())

    if args.stage in ("avatar", "heygen", "all"):
        if args.backend == "heygen" or args.stage == "heygen":
            video_path = run_heygen(script_data)
        else:
            video_path = run_avatar_local(script_data)
        run_edit(video_path, script_data)

    log("\nPipeline complete.")
    log(f"Outputs in: {OUT_DIR}")


if __name__ == "__main__":
    main()
