#!/usr/bin/env python3
"""
Rebel Campaign — Post-Processor
Runs video-edit (transcribe → copy broll_plan → render) for each reel
whose source.mp4 exists but hasn't been edited yet.

Usage:
  python3 rebel-campaign/post_process.py            # process all ready reels
  python3 rebel-campaign/post_process.py --status   # just show status
"""
from __future__ import annotations

import argparse
import hashlib
import shutil
import subprocess
import sys
from pathlib import Path

REBEL = Path(__file__).resolve().parent
REELS_DIR = REBEL / "reels"
SKILL_DIR = Path.home() / ".claude" / "skills" / "video-edit"
CACHE = Path.home() / ".cache" / "video-edit"

# Use the dedicated whisper conda env (faster-whisper, avoids numpy conflict)
WHISPER_PYTHON = "/opt/anaconda3/envs/whisper/bin/python"
REBEL_TRANSCRIBE = REBEL / "rebel_transcribe.py"

SLUGS = [
    "reel1-whose-dream",
    "reel2-the-timeline",
    "reel3-the-code",
    "reel4-the-sacrifice",
    "reel5-different-question",
]

# CAPTION_EMPHASIS phrases per reel (pipe-separated, matched to close segment)
EMPHASIS: dict[str, str] = {
    "reel1-whose-dream":      "now that you re safe|what do you want",
    "reel2-the-timeline":     "those are different objectives|never told there was a difference",
    "reel3-the-code":         "written for their threat environment|not yours",
    "reel4-the-sacrifice":    "options not obligations|the mission completing",
    "reel5-different-question": "the system was wrong|whether you re allowed to stop",
}


def workdir(source_mp4: Path) -> Path:
    """Mirror render.sh's workdir formula exactly."""
    p = source_mp4.resolve()
    digest = hashlib.sha1(str(p).encode()).hexdigest()[:12]
    return CACHE / f"{p.stem[:40]}_{digest}"


def status() -> dict[str, str]:
    """Return status for each reel: missing | audio_only | rendered | edited."""
    result = {}
    for slug in SLUGS:
        reel_dir = REELS_DIR / slug
        source   = reel_dir / "source.mp4"
        enhanced = reel_dir / "source.enhanced.mp4"
        done     = reel_dir / ".edited"
        audio    = reel_dir / "full_audio.wav"

        if done.exists():
            result[slug] = "edited ✓"
        elif enhanced.exists():
            result[slug] = "rendered (pending edit mark)"
        elif source.exists():
            result[slug] = "source_ready → needs video-edit"
        elif audio.exists():
            result[slug] = "audio_only (SadTalker pending)"
        else:
            result[slug] = "not started"
    return result


def process_one(slug: str) -> bool:
    """Run video-edit pipeline for one reel. Returns True on success."""
    reel_dir    = REELS_DIR / slug
    source_mp4  = reel_dir / "source.mp4"
    broll_plan  = reel_dir / "broll_plan.json"
    done_marker = reel_dir / ".edited"

    if done_marker.exists():
        print(f"  [{slug}] already edited, skipping")
        return True

    if not source_mp4.exists():
        print(f"  [{slug}] source.mp4 not ready yet")
        return False

    print(f"\n  [{slug}] starting video-edit pipeline...")

    # 1 — Compute workdir and stage broll_plan.json + b-roll images
    wd = workdir(source_mp4)
    wd.mkdir(parents=True, exist_ok=True)
    dest_plan = wd / "broll_plan.json"
    if broll_plan.exists():
        shutil.copy2(broll_plan, dest_plan)
        print(f"    broll_plan.json → {dest_plan}")

    # render.sh's asset stager only looks in <workdir>/broll, not reel_dir/broll
    # — copy curated scene images across so the render can find them.
    broll_dir = reel_dir / "broll"
    if broll_dir.is_dir():
        wd_broll = wd / "broll"
        wd_broll.mkdir(parents=True, exist_ok=True)
        for img in broll_dir.iterdir():
            if img.is_file():
                shutil.copy2(img, wd_broll / img.name)
        print(f"    broll/ images → {wd_broll}")

    # 2 — Transcribe (creates words.json in workdir)
    transcribe = SKILL_DIR / "scripts" / "transcribe.py"
    import os
    # Ensure homebrew ffmpeg is findable regardless of which Python runs this
    brew_bin = "/opt/homebrew/bin"
    base_path = os.environ.get("PATH", "")
    if brew_bin not in base_path:
        base_path = brew_bin + ":" + base_path
    base_env = {
        **os.environ,
        "PATH": base_path,
        # Mac OpenMP conflict when torch + conda both ship libiomp5.dylib
        "KMP_DUPLICATE_LIB_OK": "TRUE",
    }

    print(f"    transcribing {source_mp4.name}...")
    subprocess.run(
        [WHISPER_PYTHON, str(REBEL_TRANSCRIBE), str(source_mp4)],
        env=base_env,
        check=True,
    )

    # 3 — Render (preview first, then final)
    render = SKILL_DIR / "scripts" / "render.sh"
    emphasis = EMPHASIS.get(slug, "")
    env_extra = {"CAPTION_EMPHASIS": emphasis} if emphasis else {}
    env = {**base_env, **env_extra}

    print(f"    rendering preview...")
    subprocess.run(
        ["bash", str(render), str(source_mp4)],
        env=env,
        check=True,
    )

    # Copy enhanced output next to source for easy access
    enhanced_src = source_mp4.parent / (source_mp4.stem + ".enhanced.mp4")
    # render.sh writes to workdir — find it
    wd_enhanced = list(wd.glob("*.enhanced.mp4"))
    if wd_enhanced:
        shutil.copy2(wd_enhanced[-1], enhanced_src)
        print(f"    ✓ {enhanced_src.name}")

    # 4 — Mark done
    done_marker.touch()
    print(f"  [{slug}] ✓ complete")
    return True


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--status", action="store_true", help="Show status only")
    ap.add_argument("--slug", default=None, help="Process one reel by slug")
    args = ap.parse_args()

    st = status()

    print("\nRebel Campaign — Status")
    print("─" * 50)
    for slug, state in st.items():
        print(f"  {slug:<35} {state}")
    print()

    if args.status:
        return

    slugs_to_run = [args.slug] if args.slug else SLUGS
    processed = 0
    for slug in slugs_to_run:
        if st.get(slug, "").startswith("edited"):
            continue
        if st.get(slug, "") == "source_ready → needs video-edit":
            if process_one(slug):
                processed += 1

    if processed == 0:
        print("  Nothing to process right now.")
    else:
        print(f"\n  {processed} reel(s) processed.")


if __name__ == "__main__":
    main()
