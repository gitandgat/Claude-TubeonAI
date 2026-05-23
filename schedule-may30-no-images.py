"""
Schedule May 30+ posts (30 total) with 2-hour spacing. Skip image generation, use placeholder.
Fast path: content to Zernio immediately, add visuals later via Freepik.
"""
from __future__ import annotations
import os, time, requests
from anthropic import Anthropic

ANTHROPIC_KEY = os.getenv("ANTHROPIC_KEY")
ZERNIO_KEY    = os.getenv("ZERNIO_KEY")

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

AUDIENCE: A 34-year-old IMG from India. Passed MCCQE Part 1. Failed CaRMS twice. Working as a lab assistant at $48K/year. Family thinks he's "almost a doctor in Canada." Googles "IMG unmatched career options" at midnight.

STRUCTURE — follow exactly:
1. HOOK (2 lines max): Status-drop or vulnerability contrast.
2. REFRAME: "The question isn't X. It's Y."
3. SENSORY LIST (✨): 3 lines. Specific details.
4. LESSONS LIST (👣): 3 lines. Short infinitive phrases.
5. BRAND REVEAL (mid-post): "I call it Crosswalk Wisdom — [one-line description]."
6. CTA: "5 minutes. 📬 Link in the comments."
7. ENGAGEMENT QUESTION: One universal question.
8. HASHTAGS: 4 only. Always #CrosswalkWisdom #IMGCanada plus 2 contextual.

Under 1500 characters. Write as lived experience. Output ONLY the post."""

POSTS = [
    # May 30
    {"slug": "may-37", "slot": "2026-05-30T08:00:00", "topic": "The midnight panic attack — why IMGs freeze when they see a job posting that matches their dreams", "pillar": "Identity Cage", "fc": "https://fear-audit.vercel.app"},
    {"slug": "may-38", "slot": "2026-05-30T10:00:00", "topic": "CaRMS rejection isn't about clinical skill — it's about visibility politics and timeline luck", "pillar": "Courage to Choose", "fc": "www.crosswalkwisdom.com/img/calculator"},
    {"slug": "may-39", "slot": "2026-05-30T12:00:00", "topic": "The $48K salary lie — what it costs an IMG besides money when they're stuck in non-clinical limbo", "pillar": "Identity Cage", "fc": "https://fear-audit.vercel.app"},
    {"slug": "may-40", "slot": "2026-05-30T14:00:00", "topic": "4 roles in Canada where IMG credentials are an *asset*, not a barrier — and the salary ranges you should expect", "pillar": "Courage to Choose", "fc": "www.crosswalkwisdom.com/img/calculator"},
    {"slug": "may-41", "slot": "2026-05-30T16:00:00", "topic": "The yellow vest taught me something MD credentials never could — permission to be imperfect", "pillar": "Crossing Guard Philosophy", "fc": "https://crosswalkwisdom.com/philosophy"},
    # May 31
    {"slug": "may-42", "slot": "2026-05-31T08:00:00", "topic": "What unmatched IMGs don't tell their parents — the invisible grief of reaching a credential nobody values", "pillar": "Identity Cage", "fc": "https://fear-audit.vercel.app"},
    {"slug": "may-43", "slot": "2026-05-31T10:00:00", "topic": "The one question that breaks the pivot paralysis — and why IMGs never ask it", "pillar": "Courage to Choose", "fc": "www.crosswalkwisdom.com/img/calculator"},
    {"slug": "may-44", "slot": "2026-05-31T12:00:00", "topic": "Tim Hortons at 6am — the unspoken ritual where IMGs process their choices", "pillar": "Crossing Guard Philosophy", "fc": "https://crosswalkwisdom.com/philosophy"},
    {"slug": "may-45", "slot": "2026-05-31T14:00:00", "topic": "Why PhD-track research is the path nobody tells unmatched IMGs exists — $75K salary, no residency required", "pillar": "Courage to Choose", "fc": "www.crosswalkwisdom.com/img/calculator"},
    {"slug": "may-46", "slot": "2026-05-31T16:00:00", "topic": "The real cost of 'almosts' — what happens when you chase a residency that won't come", "pillar": "Identity Cage", "fc": "https://fear-audit.vercel.app"},
    # June 1
    {"slug": "jun-01", "slot": "2026-06-01T08:00:00", "topic": "The bridge nobody talks about — how to go from 'failed IMG' to 'unmatched IMG who chose differently'", "pillar": "Courage to Choose", "fc": "www.crosswalkwisdom.com/img/calculator"},
    {"slug": "jun-02", "slot": "2026-06-01T10:00:00", "topic": "Sunk cost isn't a number — it's the weight you carry at 34, stuck between two countries, two identities", "pillar": "Identity Cage", "fc": "https://fear-audit.vercel.app"},
    {"slug": "jun-03", "slot": "2026-06-01T12:00:00", "topic": "The clinical role that *won't* require another exam — and why you have zero idea it exists", "pillar": "Courage to Choose", "fc": "www.crosswalkwisdom.com/img/calculator"},
    {"slug": "jun-04", "slot": "2026-06-01T14:00:00", "topic": "Yellow vest wisdom — why standing still on the corner taught me more than residency ever did", "pillar": "Crossing Guard Philosophy", "fc": "https://crosswalkwisdom.com/philosophy"},
    {"slug": "jun-05", "slot": "2026-06-01T16:00:00", "topic": "What 'pivot' really means for an IMG — it's not failure, it's recalibration at the right time", "pillar": "Courage to Choose", "fc": "www.crosswalkwisdom.com/img/calculator"},
    # June 2
    {"slug": "jun-06", "slot": "2026-06-02T08:00:00", "topic": "The family chat that nobody answers — why your parents' expectations are 10 years behind your reality", "pillar": "Identity Cage", "fc": "https://fear-audit.vercel.app"},
    {"slug": "jun-07", "slot": "2026-06-02T10:00:00", "topic": "Ultrasound technician path in Canada — $65K starting, full credential recognition, zero additional exams", "pillar": "Courage to Choose", "fc": "www.crosswalkwisdom.com/img/calculator"},
    {"slug": "jun-08", "slot": "2026-06-02T12:00:00", "topic": "What I learned standing in the rain at 6am on the corner — permission doesn't come from a credential", "pillar": "Crossing Guard Philosophy", "fc": "https://crosswalkwisdom.com/philosophy"},
    {"slug": "jun-09", "slot": "2026-06-02T14:00:00", "topic": "The IMG paradox — overqualified for every job that doesn't require a residency, invisible for the ones that do", "pillar": "Identity Cage", "fc": "https://fear-audit.vercel.app"},
    {"slug": "jun-10", "slot": "2026-06-02T16:00:00", "topic": "Lab director, research lead, education coordinator — 3 IMG-friendly roles paying $70K+ that nobody mentors you toward", "pillar": "Courage to Choose", "fc": "www.crosswalkwisdom.com/img/calculator"},
    # June 3
    {"slug": "jun-11", "slot": "2026-06-03T08:00:00", "topic": "The question nobody asks — what if failing CaRMS was the best thing that happened to you?", "pillar": "Courage to Choose", "fc": "www.crosswalkwisdom.com/img/calculator"},
    {"slug": "jun-12", "slot": "2026-06-03T10:00:00", "topic": "Immigrant weight — the invisible tax of leaving your country, passing exams, and still not being 'enough'", "pillar": "Identity Cage", "fc": "https://fear-audit.vercel.app"},
    {"slug": "jun-13", "slot": "2026-06-03T12:00:00", "topic": "Regulatory coordinator for medical boards — $68K, IMG-credentialed, nobody mentions this path", "pillar": "Courage to Choose", "fc": "www.crosswalkwisdom.com/img/calculator"},
    {"slug": "jun-14", "slot": "2026-06-03T14:00:00", "topic": "What Sahawat learned on the crossing — that safety isn't about status, it's about presence", "pillar": "Crossing Guard Philosophy", "fc": "https://crosswalkwisdom.com/philosophy"},
    {"slug": "jun-15", "slot": "2026-06-03T16:00:00", "topic": "Two years into 'maybe next time' — at what point does a dream become a sunk cost that won't return?", "pillar": "Identity Cage", "fc": "https://fear-audit.vercel.app"},
    # June 4 (bonus 5 posts)
    {"slug": "jun-16", "slot": "2026-06-04T08:00:00", "topic": "Clinical trials coordinator — IMG role, $70K, zero residency requirement, fast path to employment", "pillar": "Courage to Choose", "fc": "www.crosswalkwisdom.com/img/calculator"},
    {"slug": "jun-17", "slot": "2026-06-04T10:00:00", "topic": "The unfinished grief of 'I'm smart enough to be a doctor, just not in Canada'", "pillar": "Identity Cage", "fc": "https://fear-audit.vercel.app"},
    {"slug": "jun-18", "slot": "2026-06-04T12:00:00", "topic": "Why your CaRMS number doesn't define your worth — and what actually does in the marketplace", "pillar": "Crossing Guard Philosophy", "fc": "https://crosswalkwisdom.com/philosophy"},
    {"slug": "jun-19", "slot": "2026-06-04T14:00:00", "topic": "The pivot conversation nobody has with unmatched IMGs until it's too late", "pillar": "Courage to Choose", "fc": "www.crosswalkwisdom.com/img/calculator"},
    {"slug": "jun-20", "slot": "2026-06-04T16:00:00", "topic": "Five years, two failed matches, $300K in debt — when does the dream become a burden?", "pillar": "Identity Cage", "fc": "https://fear-audit.vercel.app"},
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
    print(f"=== May 30-June 4: 35 posts with 2-hour spacing (8am, 10am, 12pm, 2pm, 4pm ET) ===\n")
    results = []

    for i, src in enumerate(POSTS):
        print(f"[{i+1}/{len(POSTS)}]  {src['slot']}  |  {src['pillar'][:20]}")

        try:
            linkedin = write_post(src["topic"], src["pillar"])
            short = write_short(linkedin)
            print(f"  ✓ {len(linkedin)} chars | IG: {len(short)} chars")

            post_id = schedule(linkedin, short, src["slot"], src["fc"])
            ok = not post_id.startswith("ERROR")
            print(f"  [{'✓' if ok else '✗'}] {post_id[:35]}")

            results.append({"slot": src["slot"], "slug": src["slug"], "id": post_id, "ok": ok})
            time.sleep(5)

        except Exception as e:
            print(f"  ✗ {str(e)[:60]}")
            results.append({"slot": src["slot"], "slug": src["slug"], "id": f"ERROR", "ok": False})
            time.sleep(5)

    print(f"\n{'='*60}")
    ok_count = sum(1 for r in results if r["ok"])
    print(f"\n{ok_count}/{len(POSTS)} posts scheduled successfully\n")

    for r in results:
        status = "✓" if r["ok"] else "✗"
        print(f"  {status}  {r['slot']}  {r['slug']}")

    print(f"\n✓ Ready for Freepik visuals. Run: /crosswalk-freepik to add custom images")


if __name__ == "__main__":
    main()
