#!/usr/bin/env python3
"""Local talking-head avatar generator for Crosswalk Wisdom ($0, no HeyGen/Higgsfield).

Pipeline:  vertical hook script  ->  VoiSpark voiceover (onyx)  ->  SadTalker talking head  ->  mp4

This is the free, fully-local analog to HeyGen/Higgsfield. The face is animated from a
single front-facing photo. Drop a real selfie at faces/sahawat.jpg to generate the
authentic self-clone; until then it falls back to a bundled example face so the engine
can be proven end-to-end.

Run with the avatar conda env python (has torch 2.0.1 + SadTalker deps + requests/dotenv):
    /opt/anaconda3/envs/avatar/bin/python avatar_hook.py <vertical> [--photo PATH] [--text "..."]
                                                          [--no-enhancer] [--render-only]

Verticals: crosswalk | trainer | fitness | mind | health   (or `all`)
"""
from __future__ import annotations

import argparse
import glob
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

# ── Paths ─────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent              # avatar-engine/
REPO = ROOT.parent                                  # Claude TubeonAI/
SADTALKER = ROOT / "SadTalker"
FACES = ROOT / "faces"
OUT = ROOT / "out"
AUDIO_OUT = OUT / "audio"
RESULTS = SADTALKER / "results"

# A real front-facing selfie of Sahawat goes here -> authentic self-clone.
SELF_PHOTO = FACES / "sahawat.jpg"
# Fallback so the engine runs before a real photo exists (clearly a placeholder face).
FALLBACK_PHOTO = SADTALKER / "examples" / "source_image" / "happy.png"

VOISPARK_URL = "https://api.voispark.com/api/tts/generate"

# ── Vertical hook scripts (first-person, anti-slop, ~18-22s spoken) ───────────
# These are talking-head INTROS. They hook + tee up the animation; the link lives
# in the post's first comment, never the spoken script.
HOOKS: dict[str, str] = {
    "crosswalk": (
        "A doctor told me she'd applied to the match four times. "
        "When I asked what she'd do if she stopped, she went quiet. "
        "If you're an unmatched IMG, the real question isn't how to match. "
        "It's what your training is worth outside it."
    ),
    "trainer": (
        "Most trainers count your reps. Almost none read what your body is telling them. "
        "I spent years reading bodies for a living before I ever read one in a gym. "
        "That gap is the difference between getting sore and getting stronger."
    ),
    "fitness": (
        "Most fitness advice exists to sell you something. "
        "The supplement, the program, the six-week shortcut. "
        "I trained as a physician first, so I read the study before I trust the claim. "
        "Here's what the research actually says about building muscle after forty."
    ),
    "mind": (
        "I once sat in my car for an hour before a shift, unable to walk in. "
        "Not because I couldn't do the work, but because I'd stopped recognizing who was doing it. "
        "If you're capable and still stuck, the problem isn't capacity. "
        "It's the voice in your head."
    ),
    "health": (
        "Most people treat their sixties like a waiting room. "
        "Sit still, take the pills, hope nothing breaks. "
        "The data says the opposite. The decade ahead of you answers more to what you do now "
        "than to anything on your chart. Here's where to start."
    ),
}


# ── VoiSpark voiceover ────────────────────────────────────────────────────────
def voispark_tts(text: str, out_wav: Path) -> Path:
    """Generate an onyx voiceover via VoiSpark and save it to out_wav.

    NOTE: do NOT add a `configs` key for the openai provider (error 40214).
    """
    key = os.environ.get("VOISPARK_API_KEY")
    if not key:
        raise SystemExit(
            "VOISPARK_API_KEY not found in environment / .env. "
            "Add it to the repo .env (the project already uses VoiSpark)."
        )
    resp = requests.post(
        VOISPARK_URL,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        json={
            "text": text,
            "provider": "openai",
            "model_id": "gpt-4o-mini-tts",                       # was "model" (renamed)
            "voice": {"type": "preset", "voice_id": "onyx"},     # was the bare string "onyx"
            "sync": True,
        },
        timeout=180,
    )
    resp.raise_for_status()
    payload = resp.json()
    data = payload.get("data") or {}
    if data.get("status") == "failed":
        raise SystemExit(f"VoiSpark task failed: {data.get('error')}")
    try:
        url = data["details"]["url"]
    except (KeyError, TypeError) as exc:
        raise SystemExit(f"Unexpected VoiSpark response shape: {payload}") from exc

    audio = requests.get(url, timeout=180)  # signed URL expires in ~1h -> grab now
    audio.raise_for_status()
    out_wav.parent.mkdir(parents=True, exist_ok=True)
    out_wav.write_bytes(audio.content)
    print(f"  voiceover -> {out_wav} ({out_wav.stat().st_size // 1024} KB)")
    return out_wav


# ── SadTalker render ──────────────────────────────────────────────────────────
def render_talking_head(photo: Path, wav: Path, enhancer: bool) -> Path:
    """Animate `photo` to lip-sync `wav`; return the produced mp4."""
    result_dir = RESULTS / f"hook_{int(time.time())}"
    cmd = [
        sys.executable, "inference.py",
        "--cpu",
        "--source_image", str(photo),
        "--driven_audio", str(wav),
        "--result_dir", str(result_dir),
        "--preprocess", "crop",
        "--still",                       # stable head -> reads as a steady talking-head hook
        "--size", "256",
    ]
    if enhancer:
        cmd += ["--enhancer", "gfpgan"]  # sharper face; worth the extra minute
    print(f"  rendering talking head ({'gfpgan' if enhancer else 'raw'}) ...")
    subprocess.run(cmd, cwd=SADTALKER, check=True)

    mp4s = sorted(glob.glob(str(result_dir / "**" / "*.mp4"), recursive=True),
                  key=os.path.getmtime)
    if not mp4s:
        raise SystemExit(f"SadTalker produced no mp4 in {result_dir}")
    return Path(mp4s[-1])


# ── Orchestration ─────────────────────────────────────────────────────────────
def resolve_photo(override: str | None) -> Path:
    if override:
        p = Path(override).expanduser()
        if not p.exists():
            raise SystemExit(f"--photo not found: {p}")
        return p
    if SELF_PHOTO.exists():
        return SELF_PHOTO
    print(f"  [!] No real photo at {SELF_PHOTO} — using placeholder face {FALLBACK_PHOTO.name}.")
    print("      Drop a clear, front-facing selfie at faces/sahawat.jpg for the real self-clone.")
    return FALLBACK_PHOTO


def build_one(vertical: str, photo: Path, text: str, enhancer: bool, render_only: bool) -> Path:
    print(f"\n=== {vertical} ===")
    OUT.mkdir(parents=True, exist_ok=True)
    wav = AUDIO_OUT / f"{vertical}.wav"
    if render_only and wav.exists():
        print(f"  reusing existing voiceover {wav}")
    else:
        voispark_tts(text, wav)
    mp4 = render_talking_head(photo, wav, enhancer)
    dest = OUT / f"{vertical}-avatar-hook.mp4"
    shutil.copyfile(mp4, dest)
    print(f"  ✓ {dest} ({dest.stat().st_size // 1024} KB)")
    return dest


def main() -> None:
    load_dotenv(REPO / ".env")
    ap = argparse.ArgumentParser(description="Local talking-head avatar generator")
    ap.add_argument("vertical", help="crosswalk | trainer | fitness | mind | health | all")
    ap.add_argument("--photo", default=None, help="override source face photo")
    ap.add_argument("--text", default=None, help="override spoken script (single vertical only)")
    # GFPGAN enhancer is OFF by default: under memory pressure on this 16GB Mac it
    # took ~5.5h to enhance a single 6s clip. Only enable when RAM is free.
    ap.add_argument("--enhancer", action="store_true",
                    help="GFPGAN face sharpen (VERY slow under low RAM; off by default)")
    ap.add_argument("--render-only", action="store_true", help="reuse cached voiceover wavs")
    args = ap.parse_args()

    photo = resolve_photo(args.photo)
    enhancer = args.enhancer

    if args.vertical == "all":
        for v in HOOKS:
            build_one(v, photo, HOOKS[v], enhancer, args.render_only)
        return

    if args.vertical in HOOKS:
        text = args.text or HOOKS[args.vertical]
    else:
        # Custom slug (e.g. a viral_pipeline script): allowed as long as --text is given.
        if not args.text:
            raise SystemExit(
                f"Unknown vertical '{args.vertical}'. Choose: {', '.join(HOOKS)}, all — "
                "or pass --text to render a custom slug."
            )
        text = args.text
    build_one(args.vertical, photo, text, enhancer, args.render_only)


if __name__ == "__main__":
    main()
