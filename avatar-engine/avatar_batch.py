#!/usr/bin/env python3
"""Overnight auto-batch for the local talking-head avatar.

Renders all 5 vertical avatar hooks when the Mac is idle (launchd fires this at
2 AM, wrapped in `caffeinate` so the machine stays awake for the run). On a 16GB
Mac the face renderer is slow under memory pressure, so this is designed to run
while you're not using the machine.

Behaviour:
  - Requires a real selfie at faces/sahawat.jpg. If it's missing, it logs a
    notice and exits cleanly (so it just retries the next night once you drop one)
    instead of wasting hours rendering the placeholder face.
  - Resumable: skips any vertical whose mp4 already exists, so a partial night
    picks up where it left off.
  - Reuses cached VoiSpark voiceovers across nights (only calls the API once).

Run by: com.crosswalk.avatar-batch (launchd, 2 AM daily).
"""
from __future__ import annotations

import time
from pathlib import Path

import avatar_hook as ah


def log(msg: str) -> None:
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}", flush=True)


def main() -> None:
    # load .env so VoiSpark TTS works for verticals without cached audio.
    # (avatar_hook.main() does this, but we import build_one directly — it doesn't run.)
    from dotenv import load_dotenv
    load_dotenv(ah.REPO / ".env")

    if not ah.SELF_PHOTO.exists():
        log(
            f"No selfie at {ah.SELF_PHOTO} — nothing to render. "
            "Drop a clear, front-facing photo there and this runs the next night."
        )
        return

    pending = [v for v in ah.HOOKS if not (ah.OUT / f"{v}-avatar-hook.mp4").exists()]
    if not pending:
        log(f"All {len(ah.HOOKS)} avatar hooks already rendered. Nothing to do.")
        return

    log(f"Rendering {len(pending)} pending hook(s): {', '.join(pending)}")
    for vertical in pending:
        start = time.time()
        try:
            # enhancer=False: GFPGAN is ~5.5h/6s-clip under memory pressure here, so the
            # batch renders base 256px (recognizable, $0). render_only reuses cached audio.
            ah.build_one(vertical, ah.SELF_PHOTO, ah.HOOKS[vertical],
                         enhancer=False, render_only=True)
            log(f"OK  {vertical}  ({int(time.time() - start)}s)")
        except Exception as exc:  # keep going so one bad render doesn't kill the night
            log(f"FAIL {vertical}: {exc}")
    log("Batch complete.")


if __name__ == "__main__":
    main()
