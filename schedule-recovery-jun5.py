"""
Recover 4 posts that hit Zernio 429 rate limit. Move to June 5 with 2-hour spacing.
Posts: may-39, may-40, may-41, jun-05
New slots: Jun 5 8am, 10am, 12pm, 2pm ET
"""
from __future__ import annotations
import time, requests
from anthropic import Anthropic

ANTHROPIC_KEY = "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"
ZERNIO_KEY    = "sk_d1c977cc304ec9685c24f22c7e3b868abd5a10b9db8f7648b2b74384ab1ca399"

ZERNIO_BASE = "https://zernio.com/api/v1"
ZERNIO_HDR  = {"Authorization": f"Bearer {ZERNIO_KEY}", "Content-Type": "application/json"}

LINKEDIN_ID  = "690940455f6fbb9ef8323070"
INSTAGRAM_ID = "690940655f6fbb9ef8323072"
FACEBOOK_ID  = "6909409a5f6fbb9ef8323074"
TIKTOK_ID    = "690941425f6fbb9ef8323078"
TIMEZONE     = "America/New_York"

PLACEHOLDER_IMAGE = "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=1080&h=1080&fit=crop"

anthropic = Anthropic(api_key=ANTHROPIC_KEY)

SYSTEM_PROMPT = """\
You write LinkedIn posts for Crosswalk Wisdom, a brand by Sahawat Nilwatcharamanee — a former physician who left medicine, became a crossing guard, and now helps unmatched IMGs in Canada navigate career transitions.

AUDIENCE: A 34-year-old IMG from India. Passed MCCQE Part 1. Failed CaRMS twice. Working as a lab assistant at $48K/year.

STRUCTURE — follow exactly:
1. HOOK (2 lines max): Status-drop or vulnerability contrast.
2. REFRAME: "The question isn't X. It's Y."
3. SENSORY LIST (✨): 3 lines.
4. LESSONS LIST (👣): 3 lines.
5. BRAND REVEAL (mid-post): "I call it Crosswalk Wisdom — [one-line description]."
6. CTA: "5 minutes. 📬 Link in the comments."
7. ENGAGEMENT QUESTION: One universal question.
8. HASHTAGS: 4 only. Always #CrosswalkWisdom #IMGCanada plus 2 contextual.

Under 1500 characters. Output ONLY the post."""

# 4 failed posts, recovered on June 5 with 2-hour spacing
RECOVERY_POSTS = [
    {"slug": "may-39", "new_slot": "2026-06-05T08:00:00", "topic": "The $48K salary lie — what it costs an IMG besides money when they're stuck in non-clinical limbo", "pillar": "Identity Cage", "fc": "https://fear-audit.vercel.app"},
    {"slug": "may-40", "new_slot": "2026-06-05T10:00:00", "topic": "4 roles in Canada where IMG credentials are an *asset*, not a barrier — and the salary ranges you should expect", "pillar": "Courage to Choose", "fc": "https://crosswalkwisdom.com/calculator"},
    {"slug": "may-41", "new_slot": "2026-06-05T12:00:00", "topic": "The yellow vest taught me something MD credentials never could — permission to be imperfect", "pillar": "Crossing Guard Philosophy", "fc": "https://crosswalkwisdom.com/philosophy"},
    {"slug": "jun-05", "new_slot": "2026-06-05T14:00:00", "topic": "What 'pivot' really means for an IMG — it's not failure, it's recalibration at the right time", "pillar": "Courage to Choose", "fc": "https://crosswalkwisdom.com/calculator"},
]


def write_post(topic: str, pillar: str) -> str:
    msg = anthropic.messages.create(
        model="claude-opus-4-7", max_tokens=800, system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": f"Topic: {topic}\nPillar: {pillar}\n\nWrite as Sahawat's lived experience."}]
    )
    return msg.content[0].text.strip()


def write_short(post: str) -> str:
    msg = anthropic.messages.create(
        model="claude-haiku-4-5-20251001", max_tokens=300,
        messages=[{"role": "user", "content": "Compress to 250-300 char Instagram caption. Keep hook and hashtags.\n\n" + post}]
    )
    return msg.content[0].text.strip()


def schedule(linkedin: str, short: str, slot: str, fc: str) -> str:
    body = {
        "content": linkedin,
        "mediaItems": [{"url": PLACEHOLDER_IMAGE, "type": "image"}],
        "platforms": [
            {"platform": "linkedin", "accountId": LINKEDIN_ID, "customContent": linkedin, "scheduledFor": slot, "platformSpecificData": {"firstComment": fc}},
            {"platform": "instagram", "accountId": INSTAGRAM_ID, "customContent": short, "scheduledFor": slot},
            {"platform": "facebook", "accountId": FACEBOOK_ID, "customContent": linkedin, "scheduledFor": slot},
            {"platform": "tiktok", "accountId": TIKTOK_ID, "customContent": short, "scheduledFor": slot},
        ],
        "scheduledFor": slot,
        "timezone": TIMEZONE,
    }
    r = requests.post(f"{ZERNIO_BASE}/posts", headers=ZERNIO_HDR, json=body)
    return r.json().get("post", {}).get("_id", f"ERROR:{r.status_code}")


def main():
    print("=== Recovery: 4 posts → June 5 (8am, 10am, 12pm, 2pm ET) ===\n")
    results = []

    for i, src in enumerate(RECOVERY_POSTS):
        print(f"[{i+1}/4]  {src['new_slot']}  |  {src['pillar'][:20]}")

        try:
            linkedin = write_post(src["topic"], src["pillar"])
            short = write_short(linkedin)
            print(f"  ✓ {len(linkedin)} chars")

            post_id = schedule(linkedin, short, src["new_slot"], src["fc"])
            ok = not post_id.startswith("ERROR")
            print(f"  [{'✓' if ok else '✗'}] {post_id[:35]}")

            results.append({"slug": src["slug"], "new_slot": src["new_slot"], "id": post_id, "ok": ok})
            time.sleep(5)

        except Exception as e:
            print(f"  ✗ {str(e)[:60]}")
            results.append({"slug": src["slug"], "new_slot": src["new_slot"], "id": "ERROR", "ok": False})
            time.sleep(5)

    print(f"\n{'='*50}")
    ok_count = sum(1 for r in results if r["ok"])
    print(f"\n{ok_count}/4 recovered successfully\n")
    for r in results:
        status = "✓" if r["ok"] else "✗"
        print(f"  {status}  {r['slug']}  {r['new_slot']}")
    print()


if __name__ == "__main__":
    main()
