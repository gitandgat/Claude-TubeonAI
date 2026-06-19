"""Free voice-match demo + client onboarding for the managed ghostwriting service.

The wedge: a prospect pastes their recent LinkedIn posts into a text file, you
run this, and it hands back posts written in THEIR voice — the asset that closes
the sale. It needs NO client credentials. Once they pay, the saved Client config
plus a Zernio account id is all the agent needs to start posting for them.

Usage:
  python -m linkedin_agent.onboard_client \\
      --name "Jane Doe" \\
      --niche "fractional CFO for SaaS startups" \\
      --posts-file prospects/jane.txt \\
      [--num 3] [--hashtags "#Finance #SaaS"] [--themes "a, b, c"]

posts-file: their posts separated by a line containing only ``---`` (or by blank
lines). The more real posts you paste, the sharper the voice match.
"""

from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from linkedin_agent.client_manager import (
    build_client,
    save_client,
    save_voice_profile,
)
from linkedin_agent.engine.post_writer import PostWriter
from linkedin_agent.engine.voice_clone import analyze_corpus, suggest_brief, suggest_wedge
from linkedin_agent.engine.brand_brief import write_brand_brief

FALLBACK_THEMES = (
    "a specific moment that changed how you see your work",
    "a mistake that taught you something you still use",
    "the day you decided to do things differently",
)


def split_posts(raw: str) -> list[str]:
    """Split a pasted corpus into individual posts.

    Prefers an explicit ``---`` delimiter line; otherwise falls back to
    blank-line-separated paragraphs.
    """
    if "\n---" in raw or raw.strip().startswith("---"):
        chunks = [c.strip() for c in raw.split("---")]
    else:
        chunks = [c.strip() for c in raw.split("\n\n")]
    return [c for c in chunks if c]


def write_demo_post(writer: PostWriter, theme: str) -> str:
    """Generate one demo post on a theme; return the text even if it doesn't
    pass every strict gate (a demo only needs to read like the prospect)."""
    result = writer.write_with_3_qa_rounds(hook=theme, pain_point=theme)
    return (result or {}).get("post", "").strip()


def main() -> int:
    parser = argparse.ArgumentParser(description="Voice-match demo + client onboarding")
    parser.add_argument("--name", required=True, help="Client / prospect name")
    parser.add_argument("--niche", required=True, help="What they post about")
    parser.add_argument("--posts-file", required=True, help="Text file of their past posts")
    parser.add_argument("--num", type=int, default=3, help="Demo posts to generate")
    parser.add_argument("--hashtags", default="", help='e.g. "#Finance #SaaS"')
    parser.add_argument("--themes", default="", help="Comma-separated themes (else auto)")
    parser.add_argument("--zernio-account-id", default=None,
                        help="Set only when the client goes live")
    parser.add_argument("--slug", default=None, help="Override the client slug")
    args = parser.parse_args()

    if not os.path.exists(args.posts_file):
        print(f"✗ posts-file not found: {args.posts_file}")
        return 1

    with open(args.posts_file) as f:
        posts = split_posts(f.read())
    if not posts:
        print("✗ No posts found in posts-file (separate posts with --- or blank lines)")
        return 1
    print(f"→ Loaded {len(posts)} sample posts for {args.name}")

    print("→ Cloning voice from the corpus...")
    profile = analyze_corpus(posts)
    if not profile:
        print("✗ Could not build a voice profile (AI client unavailable?). Aborting.")
        return 1
    print(f"  ✓ Voice: {profile.get('tone', 'profile built')}")

    brief = suggest_brief(args.name, args.niche)
    hashtags = args.hashtags or brief.get("hashtags", "")
    if args.themes:
        themes = tuple(t.strip() for t in args.themes.split(",") if t.strip())
    else:
        themes = tuple(brief.get("themes") or []) or FALLBACK_THEMES

    client = build_client(
        name=args.name,
        niche=args.niche,
        hashtags=hashtags,
        themes=themes,
        zernio_account_id=args.zernio_account_id,
        slug=args.slug,
    )
    save_client(client)
    save_voice_profile(client, profile)
    print(f"  ✓ Client saved: {client.data_dir}")

    # Brand brief: the Blotato-skill-readable + operator-readable context doc,
    # with the client's cloned voice + a contrarian wedge (the viral fuel).
    wedge = suggest_wedge(args.name, args.niche)
    brief_path = write_brand_brief(client, voice_profile=profile, wedge=wedge)
    print(f"  ✓ Brand brief: {brief_path}")

    writer = PostWriter(voice_profile=profile, vertical=client)

    demos: list[str] = []
    for i in range(args.num):
        theme = themes[i % len(themes)]
        print(f"\n→ Demo post {i + 1}/{args.num}: {theme}")
        post = write_demo_post(writer, theme)
        if post:
            demos.append(post)

    if not demos:
        print("✗ No demo posts generated.")
        return 1

    demo_path = os.path.join(client.data_dir, "demo_posts.md")
    with open(demo_path, "w") as f:
        f.write(f"# Voice-match demo — {client.name}\n\n_Niche: {client.niche}_\n\n")
        for i, post in enumerate(demos, 1):
            f.write(f"## Post {i}\n\n{post}\n\n---\n\n")

    print("\n" + "=" * 60)
    print(f"✓ {len(demos)} demo posts saved to {demo_path}")
    print("  Send these to the prospect as the free voice-match demo.")
    print("=" * 60 + "\n")
    for i, post in enumerate(demos, 1):
        print(f"\n----- DEMO POST {i} -----\n{post}\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
