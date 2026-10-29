#!/usr/bin/env python3
"""Generate onyx voiceovers for the 8 MoveAssess self-test videos via VoiSpark.

One WAV per composition, written to crosswalk-remotion/public/moveassess-vo-<slug>.wav
and wired into MovementTest / MovementHub with <Audio>. Narration is timed to each
video's length (test videos = 492f / 16.4s, hub = 410f / 13.7s at 30fps) so the
voice lands inside the frame window with a short tail.

Voice: onyx (deep, grounded — Sahawat's register). Verified VoiSpark schema lives
in avatar-engine/avatar_hook.py::voispark_tts. Do NOT add a `configs` key (err 40214).

Run:
    python3 generate-moveassess-voiceovers.py            # all 8
    python3 generate-moveassess-voiceovers.py single-leg # just one
"""
import os
import subprocess
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

HERE = Path(__file__).resolve().parent
load_dotenv(HERE / ".env")

VOISPARK_URL = "https://api.voispark.com/api/tts/generate"
OUT_DIR = HERE / "crosswalk-remotion" / "public"

# Narration per composition. Each maps to the on-screen beats (setup -> the tell ->
# what it means -> a light close) but speaks tighter than the captions. Kept near
# 40 words for the 16.4s test videos so onyx (~2.6 words/s) finishes with a tail.
NARRATION = {
    "single-leg": (
        "Stand on one leg for ten seconds and watch the lifted hip. "
        "If it drops, the standing glute has gone quiet and the pelvis can't stay level. "
        "That's the hidden leak behind low-back ache. Find yours, free."
    ),
    "chair-rise": (
        "Sit in a chair and stand up without your hands. No rocking, no pushing off your thighs. "
        "If you can't, your glutes and core aren't making the power. "
        "Rising unaided predicts staying independent into your seventies. Try it, free."
    ),
    "knee-cave": (
        "Arms overhead, squat, and watch your knees in a mirror. "
        "If one drifts inside your big toe, the knee isn't the problem. "
        "The hip above it stopped steering the leg. See your pattern, free."
    ),
    "forward-head": (
        "Put your back to a wall, heels and hips touching, and reach your head back with your chin level. "
        "If it won't touch without craning up, your head lives forward of your spine. "
        "Every inch loads your neck all day. Check yours, free."
    ),
    "hamstrings": (
        "Stand sideways to a mirror and check your belt line. "
        "If it tips down with a hard arch, your pelvis is tilted forward. "
        "That holds your hamstrings long, so they feel tight. Stretching misses the cause."
    ),
    "arch": (
        "Stand barefoot, feet under your hips, and look at your arches. "
        "If they sink and your ankles roll in, your base is collapsing. "
        "The shin follows, the knee caves, and your low back pays at the top. Test it, free."
    ),
    "wall-reach": (
        "Back to a wall, low back flat. Raise both arms and reach the wall overhead. "
        "If your hands miss, or your back peels off, your shoulders can't get overhead cleanly, "
        "so your spine finishes the reach. Check it, free."
    ),
    # Hub = 13.7s, keep to ~32 words.
    "hub": (
        "A wall, a chair, a mirror, sixty seconds. "
        "Seven quick checks show where your body leaks power, neck to feet. "
        "Three or more tells, you're carrying movement debt. Take all seven, free."
    ),
}


def voispark_tts(text: str, out_wav: Path) -> Path:
    key = os.environ.get("VOISPARK_API_KEY")
    if not key:
        raise SystemExit("VOISPARK_API_KEY not found in .env")
    resp = requests.post(
        VOISPARK_URL,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        json={
            "text": text,
            "provider": "openai",
            "model_id": "gpt-4o-mini-tts",
            "voice": {"type": "preset", "voice_id": "onyx"},
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
    audio = requests.get(url, timeout=180)
    audio.raise_for_status()
    out_wav.parent.mkdir(parents=True, exist_ok=True)
    out_wav.write_bytes(audio.content)
    return out_wav


def duration_seconds(wav: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(wav)],
        capture_output=True, text=True, check=True,
    )
    return float(out.stdout.strip())


# Video windows (seconds) the audio must fit inside.
LIMIT = {"hub": 410 / 30}
DEFAULT_LIMIT = 492 / 30


def main() -> int:
    only = sys.argv[1] if len(sys.argv) > 1 else None
    slugs = [only] if only else list(NARRATION.keys())
    print(f"Generating {len(slugs)} MoveAssess voiceover(s) -> {OUT_DIR}\n")
    warnings = []
    for slug in slugs:
        if slug not in NARRATION:
            print(f"  ! unknown slug {slug}")
            continue
        out = OUT_DIR / f"moveassess-vo-{slug}.wav"
        print(f"  {slug} ...", end=" ", flush=True)
        voispark_tts(NARRATION[slug], out)
        dur = duration_seconds(out)
        limit = LIMIT.get(slug, DEFAULT_LIMIT)
        fit = "OK" if dur <= limit else "OVER"
        if dur > limit:
            warnings.append((slug, dur, limit))
        print(f"{out.stat().st_size // 1024} KB · {dur:.1f}s / {limit:.1f}s [{fit}]")
    if warnings:
        print("\n⚠ Over video length (trim narration):")
        for slug, dur, limit in warnings:
            print(f"    {slug}: {dur:.1f}s > {limit:.1f}s")
        return 1
    print("\nDone. All voiceovers fit their video windows.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
