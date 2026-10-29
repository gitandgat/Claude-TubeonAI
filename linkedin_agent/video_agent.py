"""Autonomous video agent — TikTok/Reels/Shorts.

Pipeline: generate first-person caption script (learns from proven winners) →
render a silent vertical video via the Remotion TikTokReel-Dynamic composition →
return the mp4 path. Cross-posting to TikTok/IG/FB/YouTube is handled by
video_scheduler.

Silent captioned video is the PROVEN format here (the 240-594 view TikToks use
exactly this). Voiceover is a future enhancement, not required.
"""

import json
import os
import subprocess
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from linkedin_agent.engine.video_script_generator import VideoScriptGenerator

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REMOTION_DIR = os.path.join(REPO, "crosswalk-remotion")
VIDEO_OUT_DIR = os.path.join(REPO, "linkedin_agent", "data", "videos")
COMPOSITION = "TikTokReel-Dynamic"

# Rotate backgrounds so consecutive videos don't all look identical.
# Curated set + any bulk-generated bg-gen-*.jpg dropped into public/assets
# (auto-discovered — drop files in, no code edit needed).
_CURATED_BG = [
    "assets/bg-tiktok-yellow-vest.jpg",
    "assets/bg-tiktok-pov-doctor-crossing-guard.jpg",
    "assets/bg-tiktok-psychiatrist-story.jpg",
    "assets/bg-tiktok-things-people-say.jpg",
    "assets/bg-tiktok-everyone-elses-safe-place.jpg",
]


def _backgrounds() -> list:
    import glob
    assets = os.path.join(REMOTION_DIR, "public", "assets")
    gen = sorted(glob.glob(os.path.join(assets, "bg-gen-*.jpg")) +
                 glob.glob(os.path.join(assets, "bg-gen-*.png")))
    gen_rel = ["assets/" + os.path.basename(p) for p in gen]
    return _CURATED_BG + gen_rel


BACKGROUNDS = _backgrounds()


def _node_bin() -> str:
    """npx, resolved to a full path (cron's PATH omits the node bin)."""
    import shutil
    return shutil.which("npx") or "/opt/homebrew/bin/npx"


def make_video(theme: str) -> dict:
    """Generate a script and render it to an mp4. Returns {success, video_path, segments}."""
    print(f"\n🎬 Generating TikTok video for: {theme}")
    segments = VideoScriptGenerator().build_segments(theme)
    if not segments:
        return {"success": False, "error": "script generation failed"}

    total_frames = sum(s["durationFrames"] for s in segments)
    print(f"  ✓ Script: {len([s for s in segments if s['text']])} captions, ~{total_frames // 30}s")

    os.makedirs(VIDEO_OUT_DIR, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Pick by theme so a 5-video batch (same day, one process) varies — not all
    # the same background. Re-discovers bg-gen-*.jpg each call.
    bgs = _backgrounds()
    bg = bgs[hash(theme) % len(bgs)]
    props = {"segments": segments, "background": bg, "handle": "@crosswalkwisdom"}
    props_file = os.path.join(VIDEO_OUT_DIR, f"props_{stamp}.json")
    video_path = os.path.join(VIDEO_OUT_DIR, f"tiktok_{stamp}.mp4")
    with open(props_file, "w") as f:
        json.dump(props, f)

    print("  Rendering via Remotion (~1-2 min)...")
    try:
        # cron's PATH lacks the node bin — put it on PATH so npx AND the node
        # that remotion spawns internally are both findable.
        npx = _node_bin()
        env = dict(os.environ)
        env["PATH"] = os.path.dirname(npx) + os.pathsep + env.get("PATH", "")
        result = subprocess.run(
            [npx, "remotion", "render", "src/index.tsx", COMPOSITION,
             video_path, f"--props={props_file}"],
            cwd=REMOTION_DIR, capture_output=True, text=True, timeout=600, env=env,
        )
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "render timed out"}

    if result.returncode == 0 and os.path.exists(video_path):
        size_mb = os.path.getsize(video_path) / 1_000_000
        print(f"  ✓ Video rendered: {video_path} ({size_mb:.1f} MB)")
        return {"success": True, "video_path": video_path, "segments": segments,
                "theme": theme}
    print(f"  ✗ Render failed: {result.stderr[-300:]}")
    return {"success": False, "error": "render failed"}


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv(os.path.join(REPO, ".env"))
    theme = sys.argv[1] if len(sys.argv) > 1 else "The endless exam treadmill (MCCQE, NAC, English tests)"
    out = make_video(theme)
    print(json.dumps({k: v for k, v in out.items() if k != "segments"}, indent=1))
