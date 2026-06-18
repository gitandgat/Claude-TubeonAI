"""
Batch teaser generator: turn a scraped prospect CSV into one gap report per prospect.

Mines the king's videos ONCE, then loops every prospect (mine their channel ->
gap analysis -> teaser). Reuses free_sample_generator so there's one source of truth.

Note on quality: outputs use whatever the AI factory resolves to (local Ollama by
default = first-draft quality). For client-facing reports set AI_PROVIDER=claude or
run the draft through /stop-slop. Also: one king per batch is a first pass — the
strongest reports assign each prospect their own best-fit king.

Usage:
    python batch_generate.py --in scraped/tech-sales.csv \
        --king "Patrick Dang" \
        --king-channel "https://www.youtube.com/channel/UCLOzkJ9W9fntCGyYfUwMPew/videos" \
        --vertical "tech sales career" --limit 6
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from free_sample_generator import mine_channel, build_prompt, run_ai, render  # noqa: E402


def slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "prospect"


def videos_url(channel_url: str) -> str:
    return channel_url if channel_url.rstrip("/").endswith("/videos") else channel_url.rstrip("/") + "/videos"


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--in", dest="inp", required=True)
    p.add_argument("--king", required=True)
    p.add_argument("--king-channel", required=True)
    p.add_argument("--vertical", default="career")
    p.add_argument("--out-dir", default=str(HERE / "out" / "batch"))
    p.add_argument("--limit", type=int, default=10)
    args = p.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Mining king {args.king} once...")
    king_vids = mine_channel(videos_url(args.king_channel))
    print(f"  -> {len(king_vids)} videos\n")

    rows = list(csv.DictReader(Path(args.inp).open()))[: args.limit]
    written = 0
    for i, row in enumerate(rows, 1):
        name = row.get("channel") or row.get("name") or f"prospect-{i}"
        url = row.get("channel_url") or row.get("website") or ""
        if not url:
            print(f"[{i}/{len(rows)}] {name}: no channel url, skip")
            continue
        print(f"[{i}/{len(rows)}] {name}...")
        prospect_vids = mine_channel(videos_url(url))
        prompt = build_prompt(name, args.king, args.vertical, king_vids, prospect_vids)
        analysis = run_ai(prompt)
        out = out_dir / f"{slug(name)}.md"
        out.write_text(render(name, args.king, analysis, prompt, king_vids))
        written += 1
        print(f"    -> {out.name} (AI: {'filled' if analysis else 'prompt-only'})")

    print(f"\n✓ {written} teasers in {out_dir}")


if __name__ == "__main__":
    main()
