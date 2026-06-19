#!/usr/bin/env python3
"""Local, no-API repurpose fallback for when TubeonAI fails.

TubeonAI's pipeline (summarise -> repurpose x7) sometimes dies at "Preparing
audio" with status=failed. The documented fallback was MANUAL ("paste a summary,
Claude writes the 7 posts inline"). This automates that path with $0 local AI:

    source text  ->  ai_client_factory (Ollama free / Claude fallback)
                 ->  the same 7 prompts.PLATFORMS instructions
                 ->  {Title}.txt in the exact format the Zernio step consumes

Reuses what's already built: prompts.py (the platform prompts), the hook library
(grounds the LinkedIn opener), and the virality grader (advisory score on the
LinkedIn output). No TubeonAI, no new paid API.

Usage:
    python3 repurpose_local.py summary.txt --title "The Sunk Cost Trap"
    python3 repurpose_local.py --text "..." --platforms linkedin,facebook
    pbpaste | python3 repurpose_local.py --title "..."
"""

from __future__ import annotations

import argparse
import os
import sys

from prompts import PLATFORMS
from ai_client_factory import get_ai_client
from linkedin_agent.engine.hook_library import frameworks_block
from linkedin_agent.engine.virality_grader import grade as grade_virality

SECTION_RULE = "=" * 60

SYSTEM = """You are Dr. Sahawat, writing for Crosswalk Wisdom. You repurpose one piece of source content into platform-native social copy. First person, warm, grounded, direct, never preachy. Write as original lived experience and never mention the source or "the video".

HARD BANS:
- No AI slop: unleash, dive into, game-changer, supercharge, transformative, leverage, empower, unlock, cutting edge, paradigm shift, "here's what I learned", "at the end of the day", "honestly", "literally", "let's be real".
- No em dashes. Use commas or periods.
- No meta section labels (HOOK:, CTA:) UNLESS the platform format explicitly asks for cues like [Slide N], [VISUAL], or [ON SCREEN TEXT].

Follow the platform instructions exactly. Output ONLY the post copy, nothing else."""


def derive_title(source: str, explicit: str | None, src_path: str | None) -> str:
    """Best-effort human title: explicit > first source line > filename > default."""
    if explicit:
        return explicit.strip()
    first = next((ln.strip() for ln in source.splitlines() if ln.strip()), "")
    if first:
        return (first[:70] + "...") if len(first) > 73 else first
    if src_path:
        return os.path.splitext(os.path.basename(src_path))[0].replace("_", " ").title()
    return "Repurposed Content"


def format_output(title: str, sections: list[tuple[str, str]]) -> str:
    """Render the {Title}.txt the downstream Zernio scheduler reads.

    Matches the layout the TubeonAI pipeline produces: a title header, then one
    ruled block per platform.
    """
    parts = [f"# {title}", ""]
    for label, content in sections:
        parts += [SECTION_RULE, f"## {label}", SECTION_RULE, "", content.strip(), ""]
    return "\n".join(parts) + "\n"


def _generate(provider, client, user: str, max_tokens: int = 1500) -> str:
    """One AI call, mirroring the dual interface used across the agent."""
    if provider == "claude":
        resp = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=max_tokens,
            system=SYSTEM,
            messages=[{"role": "user", "content": user}],
        )
    else:
        resp = client.create(
            messages=[{"role": "user", "content": user}],
            system=SYSTEM,
            max_tokens=max_tokens,
        )
    return resp.content[0].text.strip()


def repurpose(source: str, title: str | None = None,
              platforms: list[str] | None = None) -> dict:
    """Generate platform copy locally. Returns {title, sections, virality}."""
    if not source.strip():
        raise ValueError("Empty source content — nothing to repurpose.")

    keys = platforms or list(PLATFORMS.keys())
    unknown = [k for k in keys if k not in PLATFORMS]
    if unknown:
        raise ValueError(f"Unknown platform(s): {unknown}. Known: {list(PLATFORMS)}")

    provider, client = get_ai_client()
    sections: list[tuple[str, str]] = []
    virality = None

    for key in keys:
        spec = PLATFORMS[key]
        label = spec["label"]
        print(f"  → {label} ({key})...")

        # Ground the LinkedIn opener in a proven hook framework.
        grounding = ""
        if key == "linkedin":
            fw = frameworks_block(title or source[:120])
            if fw:
                grounding = f"\n\n{fw}"

        user = (f"{spec['prompt']}{grounding}\n\n"
                f"SOURCE CONTENT:\n{source}")
        try:
            content = _generate(provider, client, user)
        except Exception as e:
            print(f"    ✗ {key} failed: {e}")
            continue

        sections.append((label, content))

        # Advisory virality grade on the LinkedIn output (hook = 50%).
        if key == "linkedin":
            v_score, v_dims, v_fixes = grade_virality(content)
            virality = {"score": v_score, "dims": v_dims, "fixes": v_fixes}
            mark = "✓" if v_score >= 70 else "~ advisory"
            print(f"    virality {v_score}/100 (hook {v_dims['hook']}/10) {mark}")

    return {"title": title, "sections": sections, "virality": virality}


def _read_source(args) -> tuple[str, str | None]:
    """Resolve source text from a file arg, --text, or stdin."""
    if args.source and os.path.exists(args.source):
        with open(args.source, "r") as f:
            return f.read(), args.source
    if args.text:
        return args.text, None
    if not sys.stdin.isatty():
        return sys.stdin.read(), None
    raise SystemExit("No source. Pass a file, --text \"...\", or pipe via stdin.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Local no-API repurpose fallback.")
    parser.add_argument("source", nargs="?", help="Source text file (summary/transcript).")
    parser.add_argument("--text", help="Source text passed inline.")
    parser.add_argument("--title", help="Title for the output file/header.")
    parser.add_argument("--platforms", help="Comma-separated subset (default: all 7).")
    parser.add_argument("--out", help="Output path (default: '<title>.txt').")
    args = parser.parse_args()

    source, src_path = _read_source(args)
    title = derive_title(source, args.title, src_path)
    platforms = [p.strip() for p in args.platforms.split(",")] if args.platforms else None

    print(f"\nRepurposing locally (no TubeonAI): {title}")
    result = repurpose(source, title=title, platforms=platforms)

    if not result["sections"]:
        raise SystemExit("✗ No platform output generated.")

    out_path = args.out or f"{title}.txt"
    with open(out_path, "w") as f:
        f.write(format_output(title, result["sections"]))

    print(f"\n✓ {len(result['sections'])}/{len(platforms or PLATFORMS)} platforms → {out_path}")
    if result["virality"]:
        v = result["virality"]
        print(f"  LinkedIn virality: {v['score']}/100 (hook {v['dims']['hook']}/10)")
        for fix in v["fixes"][:3]:
            print(f"    • {fix}")
    print("\nNext: schedule with your Zernio step (see /tubeonai-repurpose Step 2).")


if __name__ == "__main__":
    main()
