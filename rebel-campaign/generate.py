#!/usr/bin/env python3
"""
Rebel Campaign — Automated Reel Generator
"The First Generation to Choose"

Pipeline per reel:
  1. VoiSpark → full_audio.wav (complete reel script, plays under everything)
  2. VoiSpark → hook_audio.wav (hook segment only, used to drive the avatar)
  3. SadTalker → short_avatar.mp4 (AVATAR_DURATION_SEC cold-open only — the
     avatar never returns; everything after is curated b-roll scenes)
  4. ffmpeg → filler_video.mp4 (256x256 held frame, covers the post-cutaway
     span so concat works; invisible — fully covered by broll_plan takeovers)
  5. ffmpeg → source.mp4 (short_avatar + filler, full_audio.wav muxed in)
  6. Hand-author broll_plan.json: full-screen `static` Mystic-generated
     scenes from AVATAR_DURATION_SEC to the end (video-edit skill post-proc)

Renders are STRICTLY SEQUENTIAL — one SadTalker job at a time. Only ONE
avatar clip per reel now (no close_avatar) — roughly half the SadTalker
compute of the old hook+close design.

Usage:
  /opt/anaconda3/envs/avatar/bin/python rebel-campaign/generate.py
  /opt/anaconda3/envs/avatar/bin/python rebel-campaign/generate.py --reel reel1-whose-dream
  /opt/anaconda3/envs/avatar/bin/python rebel-campaign/generate.py --audio-only  # skip SadTalker
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

# Reuse VoiSpark + SadTalker from avatar_hook.py
AVATAR_ENGINE = Path(__file__).resolve().parent.parent / "avatar-engine"
sys.path.insert(0, str(AVATAR_ENGINE))
from avatar_hook import voispark_tts, render_talking_head, SELF_PHOTO  # type: ignore

from scripts import REELS  # type: ignore

ROOT = Path(__file__).resolve().parent
REELS_DIR = ROOT / "reels"
FACE = SELF_PHOTO  # faces/sahawat.jpg

# SadTalker render lock (machine-global, same convention as video-edit skill)
RENDER_LOCK = Path("/tmp/video-edit-render.lock")

# How long the avatar stays on screen before the permanent cut to generated
# b-roll scenes. SadTalker is fixed --size 256, so the filler segment below
# is scaled/cropped to match exactly — mismatched resolutions silently
# corrupt the concat (caught June 24 2026: the old static middle segment was
# 2048x2048 against SadTalker's 256x256 and nobody noticed because b-roll
# overlays usually covered it).
AVATAR_DURATION_SEC = 4.0
AVATAR_SIZE = 256


# ── Helpers ───────────────────────────────────────────────────────────────────

def probe_duration(path: Path) -> float:
    """Return duration of an audio/video file in seconds via ffprobe."""
    out = subprocess.check_output(
        [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        stderr=subprocess.DEVNULL,
    )
    return float(out.strip())


def wait_for_lock(timeout: int = 7200) -> None:
    """Block until the SadTalker render lock is free (max timeout seconds)."""
    waited = 0
    while RENDER_LOCK.exists():
        if waited == 0:
            print("  [lock] waiting for previous SadTalker render to finish...")
        time.sleep(10)
        waited += 10
        if waited > timeout:
            raise TimeoutError("SadTalker render lock held > 2 hours — check for stalled processes")


def trim_audio(src_wav: Path, duration: float, out_wav: Path) -> None:
    """Cut the first `duration` seconds of `src_wav` (used to drive the short avatar clip)."""
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(src_wav), "-t", str(duration), "-c", "copy", str(out_wav)],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


FILLER_COLOR = "0x1A1A1A"  # Crosswalk Wisdom charcoal (matches RAISIN in the
                            # video-edit skill's own templates) — used wherever
                            # a word_pop beat has no static scene under it
                            # (close_gaps.py can't reconcile a non-partial
                            # `static` beat overlapping a `word_pop`, so those
                            # windows fall through to this filler instead).
                            # A flat brand-dark card reads as a deliberate
                            # "punch panel" for the kinetic text, not a glitch.


def build_filler_video(duration: float, out: Path) -> None:
    """Hold a solid charcoal frame for `duration` seconds, at AVATAR_SIZE so it
    concats cleanly with the SadTalker clip. No audio track — the final mux
    replaces audio with full_audio.wav, so this segment's audio is irrelevant.
    Mostly invisible: curated broll_plan.json `static` scenes cover most of
    it; word_pop windows (which can't have a static scene under them) show
    this charcoal card directly."""
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", f"color=c={FILLER_COLOR}:size={AVATAR_SIZE}x{AVATAR_SIZE}:rate=25",
            "-t", str(duration),
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-an",
            str(out),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def stitch_source(
    short_avatar_mp4: Path,
    filler_mp4: Path,
    full_audio: Path,
    out: Path,
) -> None:
    """Concat short avatar + filler video tracks, replace audio with full_audio."""
    avatar_v = out.parent / "short_avatar_v.mp4"
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(short_avatar_mp4), "-an", "-c:v", "copy", str(avatar_v)],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    concat_list = out.parent / "concat.txt"
    concat_list.write_text(f"file '{avatar_v}'\nfile '{filler_mp4}'\n")
    video_only = out.parent / "video_only.mp4"
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0", "-i", str(concat_list),
            "-c", "copy",
            str(video_only),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    # Replace audio with full reel voice track
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", str(video_only),
            "-i", str(full_audio),
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "192k",
            "-map", "0:v:0", "-map", "1:a:0",
            "-shortest",
            str(out),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    avatar_v.unlink(missing_ok=True)
    concat_list.unlink(missing_ok=True)
    video_only.unlink(missing_ok=True)


def build_broll_plan(reel: dict, timings: dict) -> list[dict]:
    """
    Build broll_plan.json entries with real appear_sec values derived from
    the WAV timings (hook_dur, middle_dur, close_dur, total_dur).

    The video-edit skill's align_to_speech.py will snap timings to the
    transcript using speech_anchor fields — these are initial estimates.
    """
    hook_dur: float = timings["hook_dur"]
    middle_dur: float = timings["middle_dur"]
    close_start: float = hook_dur + middle_dur

    plan: list[dict] = []

    for overlay in reel["overlays"]:
        kind = overlay["kind"]

        reason = overlay.get("reason", "Visual support for the spoken idea")

        if kind == "hook_title":
            plan.append({
                "kind": "hook_title",
                "start_sec": 0.5,
                "end_sec": min(hook_dur - 0.5, 4.0),
                "align": overlay["align"],
                "left_text": overlay["left_text"],
                "right_text": overlay["right_text"],
                "speech_anchor": overlay["speech_anchor"],
                "vertical": overlay["vertical"],
                "behind_subject": overlay.get("behind_subject", True),
                "reason": reason,
            })

        elif kind == "stat_punch":
            plan.append({
                "kind": "stat_punch",
                "start_sec": hook_dur * 0.6,
                "end_sec": hook_dur * 0.6 + 3.5,
                "value": overlay["value"],
                "caption": overlay["caption"],
                "speech_anchor": overlay["speech_anchor"],
                "reason": reason,
            })

        elif kind == "vertical_timeline":
            # Spans the middle section
            tl_start = hook_dur + 1.0
            tl_end = hook_dur + middle_dur - 1.0
            tl_span = tl_end - tl_start
            steps = overlay["steps"]
            step_gap = tl_span / len(steps)
            plan.append({
                "kind": "vertical_timeline",
                "start_sec": tl_start,
                "end_sec": tl_end,
                "speech_anchor": overlay["speech_anchor"],
                "reason": reason,
                "steps": [
                    {
                        "heading": s["heading"],
                        "description": s["description"],
                        "appear_sec": tl_start + i * step_gap,
                    }
                    for i, s in enumerate(steps)
                ],
            })

        elif kind == "vs_split":
            # Place in middle or close depending on speech_anchor position
            vs_start = hook_dur + middle_dur * 0.5
            plan.append({
                "kind": "vs_split",
                "start_sec": vs_start,
                "end_sec": vs_start + 5.0,
                "speech_anchor": overlay["speech_anchor"],
                "top_label": overlay["top_label"],
                "top_items": overlay["top_items"],
                "bottom_label": overlay["bottom_label"],
                "bottom_items": overlay["bottom_items"],
                "reason": reason,
            })

        elif kind == "image_card":
            ic_start = hook_dur + 1.5
            plan.append({
                "kind": "image_card",
                "start_sec": ic_start,
                "end_sec": ic_start + 5.0,
                "speech_anchor": overlay["speech_anchor"],
                "image_path": f"broll/{reel['slug']}-family.jpg",
                "caption": overlay.get("caption", ""),
                "reason": reason,
            })

        elif kind == "word_pop":
            # Distribute word_pops across their natural section
            items = overlay["items"]
            # Estimate position from speech_anchor keyword (hook vs middle vs close)
            anchor = overlay["speech_anchor"].lower()
            hook_words = reel["hook_text"].lower()
            close_words = reel["close_text"].lower()
            first_word = anchor.split()[0]
            if first_word in hook_words:
                base = hook_dur * 0.5
            elif first_word in close_words:
                base = close_start + 1.0
            else:
                base = hook_dur + middle_dur * 0.4

            plan.append({
                "kind": "word_pop",
                "start_sec": base,
                "end_sec": base + 1.5 * len(items) + 1.0,
                "speech_anchor": overlay["speech_anchor"],
                "vertical": overlay.get("vertical", 0.72),
                "reason": reason,
                "items": [
                    {"text": item["text"], "appear_sec": base + item["offset_sec"]}
                    for item in items
                ],
            })

    return plan


# ── Per-reel pipeline ──────────────────────────────────────────────────────────

def process_reel(reel: dict, audio_only: bool = False) -> None:
    slug = reel["slug"]
    reel_dir = REELS_DIR / slug
    reel_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"  REEL: {reel['title']} ({slug})")
    print(f"{'='*60}")

    # 1 ── Generate audio files via VoiSpark ───────────────────────────────────
    full_wav   = reel_dir / "full_audio.wav"
    hook_wav   = reel_dir / "hook_audio.wav"
    close_wav  = reel_dir / "close_audio.wav"
    middle_wav = reel_dir / "middle_audio.wav"

    full_script = (
        reel["hook_text"] + " " +
        reel["middle_text"] + " " +
        reel["close_text"]
    )

    for label, wav, text in [
        ("full",   full_wav,   full_script),
        ("hook",   hook_wav,   reel["hook_text"]),
        ("middle", middle_wav, reel["middle_text"]),
        ("close",  close_wav,  reel["close_text"]),
    ]:
        if wav.exists():
            print(f"  [cache] {label} audio exists, skipping VoiSpark call")
        else:
            print(f"  [voice] generating {label} audio via VoiSpark...")
            voispark_tts(text, wav)

    # Measure durations
    hook_dur   = probe_duration(hook_wav)
    middle_dur = probe_duration(middle_wav)
    close_dur  = probe_duration(close_wav)
    total_dur  = probe_duration(full_wav)
    timings = {
        "hook_dur": hook_dur,
        "middle_dur": middle_dur,
        "close_dur": close_dur,
        "total_dur": total_dur,
        "close_start": hook_dur + middle_dur,
    }
    print(f"  durations: hook={hook_dur:.1f}s  middle={middle_dur:.1f}s  "
          f"close={close_dur:.1f}s  total={total_dur:.1f}s")
    (reel_dir / "timings.json").write_text(json.dumps(timings, indent=2))

    if audio_only:
        print("  [audio-only mode] skipping SadTalker + stitch")
        _write_broll_plan(reel, reel_dir, timings)
        return

    # 2 ── SadTalker — ONE short avatar clip, then permanent cut to b-roll ─────
    # Avatar carries the cold open only; the rest of the reel (rest of hook +
    # middle + close) plays over curated Mystic-generated scenes in
    # broll_plan.json (kind "static", full-screen Ken Burns takeover). No
    # close-avatar render — cuts SadTalker compute roughly in half per reel.
    avatar_dur = min(AVATAR_DURATION_SEC, hook_dur)
    short_avatar = reel_dir / "short_avatar.mp4"
    if not short_avatar.exists():
        hook_short_wav = reel_dir / "hook_short.wav"
        trim_audio(hook_wav, avatar_dur, hook_short_wav)
        wait_for_lock()
        print(f"  [avatar] rendering {avatar_dur:.1f}s cold-open talking head...")
        mp4 = render_talking_head(FACE, hook_short_wav, enhancer=False)
        shutil.copyfile(mp4, short_avatar)
        print(f"  ✓ {short_avatar.name} ({short_avatar.stat().st_size // 1024} KB)")

    # 3 ── Build filler segment for everything after the cutaway ──────────────
    # Never actually seen on screen — fully covered by full-screen broll_plan
    # takeovers — but must match SadTalker's fixed 256x256 so concat is clean.
    filler_video = reel_dir / "filler_video.mp4"
    filler_dur = max(0.1, total_dur - avatar_dur)
    if not filler_video.exists():
        print("  [ffmpeg] building filler segment for post-cutaway b-roll...")
        build_filler_video(filler_dur, filler_video)

    # 4 ── Stitch source.mp4 ───────────────────────────────────────────────────
    source_mp4 = reel_dir / "source.mp4"
    if not source_mp4.exists():
        print("  [ffmpeg] stitching source.mp4...")
        stitch_source(short_avatar, filler_video, full_wav, source_mp4)
        print(f"  ✓ source.mp4 ({source_mp4.stat().st_size // 1024} KB)")

    # 5 ── Write broll_plan.json (only if one isn't already hand-curated) ──────
    _write_broll_plan(reel, reel_dir, timings)
    print(f"  ✓ {slug} complete — source.mp4 ready for video-edit")


def _write_broll_plan(reel: dict, reel_dir: Path, timings: dict) -> None:
    plan_path = reel_dir / "broll_plan.json"
    if plan_path.exists():
        print(f"  [skip] broll_plan.json already exists (hand-curated) — not overwriting")
        return
    plan = build_broll_plan(reel, timings)
    plan_path.write_text(json.dumps(plan, indent=2))
    print(f"  ✓ broll_plan.json ({len(plan)} beats)")


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")

    ap = argparse.ArgumentParser(description="Rebel campaign reel generator")
    ap.add_argument("--reel", default=None, help="Process a single reel by slug")
    ap.add_argument(
        "--audio-only",
        action="store_true",
        help="Generate voice audio and broll_plan only; skip SadTalker render",
    )
    args = ap.parse_args()

    reels_to_run = (
        [r for r in REELS if r["slug"] == args.reel]
        if args.reel
        else REELS
    )
    if not reels_to_run:
        raise SystemExit(f"No reel found with slug '{args.reel}'")

    print(f"\nRebel Campaign Generator")
    print(f"Reels to process: {len(reels_to_run)}")
    print(f"Mode: {'audio-only' if args.audio_only else 'full (audio + avatar + stitch)'}")
    print(f"Face: {FACE}")

    for reel in reels_to_run:
        process_reel(reel, audio_only=args.audio_only)

    print("\n\nAll reels complete.")
    print("Next: run video-edit skill on each source.mp4 with its broll_plan.json")
    print("  cd ~/.claude/skills/video-edit")
    print(f"  bash scripts/transcribe.py '{REELS_DIR}/reel1-whose-dream/source.mp4'")
    print(f"  CAPTION_EMPHASIS='now that you re safe|what do you want' \\")
    print(f"    bash scripts/render.sh '{REELS_DIR}/reel1-whose-dream/source.mp4'")


if __name__ == "__main__":
    main()
