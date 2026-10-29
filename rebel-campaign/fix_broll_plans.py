#!/usr/bin/env python3
"""
One-time fixer:
1. Adds `reason` to every beat entry in broll_plan.json files for ready reels.
2. Creates placeholder b-roll images for image_card entries.
3. Resets broll_plan.source.json to match (so render.sh picks up the fix).
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
from pathlib import Path

REBEL = Path(__file__).resolve().parent
REELS_DIR = REBEL / "reels"
CACHE = Path.home() / ".cache" / "video-edit"

BREW_BIN = "/opt/homebrew/bin"

SLUGS = [
    "reel1-whose-dream",
    "reel2-the-timeline",
    "reel3-the-code",
]

DEFAULT_REASONS: dict[str, str] = {
    "hook_title": "Opens with the core tension to hook in the first 2 seconds",
    "word_pop":   "Kinetic text amplifies the verbal punch — burns the idea into memory",
    "image_card": "Visual proof point grounds the abstract claim in a real scenario",
    "stat_punch": "Shocking number creates pattern interrupt and social share motivation",
    "vs_split":   "Side-by-side contrast makes the gap between old and new reality visceral",
    "vertical_timeline": "Sequential steps show the hidden systemic pressure building over time",
}


def workdir_for(source_mp4: Path) -> Path:
    p = source_mp4.resolve()
    digest = hashlib.sha1(str(p).encode()).hexdigest()[:12]
    return CACHE / f"{p.stem[:40]}_{digest}"


def make_placeholder_image(out_path: Path) -> None:
    """Create a 1080x1920 dark gradient placeholder image via ffmpeg."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    env = {**os.environ, "PATH": BREW_BIN + ":" + os.environ.get("PATH", "")}
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", "color=c=0x1a1a2e:size=1080x1920:rate=1",
            "-frames:v", "1",
            str(out_path),
        ],
        env=env,
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    print(f"  created placeholder: {out_path.name}")


def fix_plan(plan_path: Path, workdir: Path) -> None:
    beats: list[dict] = json.loads(plan_path.read_text())
    changed = False

    for beat in beats:
        kind = beat.get("kind", "")

        # Add reason if missing
        if not beat.get("reason"):
            beat["reason"] = DEFAULT_REASONS.get(kind, "Visual support for the spoken idea")
            changed = True

        # Ensure image_card images exist
        if kind == "image_card" and beat.get("image_path"):
            img_name = Path(beat["image_path"]).name
            broll_dir = workdir / "broll"
            broll_dir.mkdir(parents=True, exist_ok=True)
            placeholder = broll_dir / img_name
            if not placeholder.exists():
                make_placeholder_image(placeholder)
                changed = True

    if changed:
        text = json.dumps(beats, indent=2)
        plan_path.write_text(text)
        # Also reset broll_plan.source.json so render.sh adopts the changes
        src_plan = plan_path.parent / "broll_plan.source.json"
        src_plan.write_text(text)
        print(f"  updated {plan_path.name} ({len(beats)} beats)")
    else:
        print(f"  {plan_path.name} already clean")


def main() -> None:
    for slug in SLUGS:
        reel_dir = REELS_DIR / slug
        source_mp4 = reel_dir / "source.mp4"
        if not source_mp4.exists():
            print(f"[skip] {slug} — no source.mp4")
            continue

        wd = workdir_for(source_mp4)

        # Fix the reel's own broll_plan.json (always do this)
        reel_plan = reel_dir / "broll_plan.json"
        print(f"\n[{slug}]")
        if reel_plan.exists():
            wd.mkdir(parents=True, exist_ok=True)
            fix_plan(reel_plan, wd)

        # Also fix workdir copy if it exists
        wd_plan = wd / "broll_plan.json"
        if wd_plan.exists() and wd_plan != reel_plan:
            fix_plan(wd_plan, wd)

    print("\nDone. Re-run post_process.py to render.")


if __name__ == "__main__":
    main()
