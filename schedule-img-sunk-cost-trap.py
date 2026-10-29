"""
Schedule: IMG Sunk Cost Trap — April 16 2026
Slots: 2pm · 5pm · 8pm ET

Post 1 — 14:00 ET — LinkedIn static image (LI/IG/FB/TT, NO YouTube — image-only)
Post 2 — 17:00 ET — Instagram carousel video (all 5 platforms)
Post 3 — 20:00 ET — Story Reel video (all 5 platforms)
"""
import os, time, requests

BASE    = "https://zernio.com/api/v1"
from zernio_key import ZERNIO_API_KEY as API_KEY
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

LINKEDIN_ID  = "690940455f6fbb9ef8323070"
INSTAGRAM_ID = "690940655f6fbb9ef8323072"
FACEBOOK_ID  = "6909409a5f6fbb9ef8323074"
TIKTOK_ID    = "690941425f6fbb9ef8323078"
YOUTUBE_ID   = "690940d35f6fbb9ef8323077"
TZ = "America/New_York"

OUT = "/Users/toto/Claude TubeonAI/crosswalk-remotion/out"

# ─── Media files ──────────────────────────────────────────────────────────────

POSTS = [
    {
        "label":     "LinkedIn image — Sunk Cost Trap stat visual",
        "file":      f"{OUT}/linkedin-sunk-cost-trap.png",
        "mime":      "image/png",
        "media_type":"image",
        "time":      "2026-04-16T14:00:00",
        "youtube":   False,
        "yt_title":  None,
        "li": """\
You moved to Canada to become a doctor.

Now you're afraid that stopping means you failed everyone who believed in you.

The question isn't: "How do I not disappoint them?"

It's: "Who are you already disappointing?"

👣 The version of you who stayed up until 3am studying MCCQE while your friends built careers.
👣 The version who told your family "one more year" — for the third time.
👣 The version who moved to a new country on a dream and deserves a real life in return.
👣 The version who already knows the math doesn't work — but can't say it out loud.

Match rate for Canadian medical graduates: 97%
Match rate for IMGs: 10–22%

This isn't a skill gap.
It's a structural problem.

The 4 layers keeping you on the treadmill:
✨ Financial — "$25,000+ already spent. I can't waste it."
✨ Time — "I've given years. I can't start over."
✨ Identity — "I AM a doctor. What am I without that?"
✨ Immigration — "If I stop, I lose Canada."

(That last one has a key. NOC codes for non-clinical roles preserve your Express Entry eligibility. Nobody told you that.)

The disappointment you're carrying isn't theirs.

It belongs to the person who keeps saying "one more year" to a system giving 80% of them nothing in return.

That person is you. And you deserve better than that.

I was an IMG. I ran the treadmill. Crosswalk Wisdom exists for the 80% who aren't being served by "try harder."

Free MCCQE Reality Calculator — 5 minutes, real math, not hope math.

Link in the comments.

Have you ever stayed in something long after it stopped making sense — because leaving felt like betrayal? Not of yourself. Of everyone watching.

What's the weight of that?

#IMGCanada #SunkCostTrap #CrosswalkWisdom #MedicalPivot""",
        "ig": """\
The match rate nobody showed you before you started the pathway.

Canadian graduates: 97%
IMGs: 10–22%

This is not a skill gap.
This is a structural failure.

And the person already being let down every year you stay on the treadmill?

That's you.

Free MCCQE Reality Calculator → link in bio.

#IMGCanada #SunkCostTrap #CrosswalkWisdom #MedicalPivot""",
    },
    {
        "label":     "Instagram carousel — The Sunk Cost Trap (6 slides)",
        "file":      f"{OUT}/sunk-cost-trap-carousel.mp4",
        "mime":      "video/mp4",
        "media_type":"video",
        "time":      "2026-04-16T17:00:00",
        "youtube":   True,
        "yt_title":  "The Sunk Cost Trap: What 80% of IMGs in Canada were never told",
        "li": """\
80% of IMGs won't match.

The system always knew.
Nobody told you.

The 4 locks keeping you on the treadmill — and what the math actually says.

Free MCCQE Reality Calculator → link in comments.

#IMGCanada #SunkCostTrap #CrosswalkWisdom #MedicalPivot""",
        "ig": """\
80% of IMGs won't match.

The system always knew.
Nobody told you.

Swipe to see the 4 locks keeping you on the treadmill — and how to break them.

Free MCCQE Reality Calculator → link in bio.

#IMGCanada #SunkCostTrap #CrosswalkWisdom #MedicalPivot""",
    },
    {
        "label":     "Story Reel — The Morning Nobody Knew My Name",
        "file":      f"{OUT}/story-reel-morning.mp4",
        "mime":      "video/mp4",
        "media_type":"video",
        "time":      "2026-04-16T20:00:00",
        "youtube":   True,
        "yt_title":  "I was a doctor. Now I'm a crossing guard. Here's why.",
        "li": """\
"I was a doctor."

Then I became a crossing guard in Canada.

Not because I failed.

Because I finally chose something instead of surviving something.

That is the difference.

If you're an IMG wondering whether the treadmill is still worth it — this is for you.

#CrosswalkWisdom #BurnoutRecovery #IMGCanada #CareerPivot""",
        "ig": """\
"I was a doctor."

Then I became a crossing guard in Canada.

Not because I failed.

Because I finally chose something instead of surviving something.

That is the difference.

#CrosswalkWisdom #BurnoutRecovery #IMGCanada #CareerPivot""",
    },
]


# ─── Helpers ──────────────────────────────────────────────────────────────────

def upload_media(filepath, mime):
    ext = os.path.splitext(filepath)[1].lstrip(".")
    filename = os.path.basename(filepath)
    filesize = os.path.getsize(filepath)
    r = requests.post(
        f"{BASE}/media/presign",
        headers=HEADERS,
        json={"filename": filename, "contentType": mime, "fileSize": filesize},
    )
    r.raise_for_status()
    data = r.json()
    upload_url = data["uploadUrl"]
    public_url = data["publicUrl"]
    with open(filepath, "rb") as f:
        put_r = requests.put(upload_url, data=f, headers={"Content-Type": mime})
        put_r.raise_for_status()
    return public_url


def create_post(post, media_url):
    li  = post["li"]
    ig  = post["ig"]
    fb  = li
    tt  = ig
    yt_desc = li + "\n\n#Shorts #CrosswalkWisdom #IMGCanada #SunkCostTrap #MedicalPivot"

    media_item = {"url": media_url, "type": post["media_type"]}

    platforms = [
        {"platform": "linkedin",  "accountId": LINKEDIN_ID,  "customContent": li, "scheduledFor": post["time"]},
        {"platform": "instagram", "accountId": INSTAGRAM_ID, "customContent": ig, "scheduledFor": post["time"]},
        {"platform": "facebook",  "accountId": FACEBOOK_ID,  "customContent": fb, "scheduledFor": post["time"]},
        {"platform": "tiktok",    "accountId": TIKTOK_ID,    "customContent": tt, "scheduledFor": post["time"]},
    ]

    if post["youtube"]:
        platforms.append({
            "platform":    "youtube",
            "accountId":   YOUTUBE_ID,
            "customContent": yt_desc,
            "title":       post["yt_title"],
            "scheduledFor": post["time"],
        })

    body = {
        "content":     li,
        "mediaItems":  [media_item],
        "platforms":   platforms,
        "scheduledFor": post["time"],
        "timezone":    TZ,
    }

    r = requests.post(f"{BASE}/posts", headers=HEADERS, json=body)
    return r.status_code, r.text[:400]


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    print("Scheduling IMG Sunk Cost Trap — April 16 2026\n")

    for post in POSTS:
        print(f"[{post['time']} ET] {post['label']}")

        if not os.path.exists(post["file"]):
            print(f"  [SKIP] File not found: {post['file']}\n")
            continue

        # 1. Upload
        try:
            url = upload_media(post["file"], post["mime"])
            print(f"  [UPLOAD OK] {url[:60]}...")
        except Exception as e:
            print(f"  [UPLOAD FAIL] {e}\n")
            continue

        # 2. Create post
        status, body = create_post(post, url)
        platforms = "LI/IG/FB/TT" + ("/YT" if post["youtube"] else "")
        if status in (200, 201):
            print(f"  [POST OK {status}] {platforms}\n")
        else:
            print(f"  [POST FAIL {status}] {body}\n")

        time.sleep(1.5)

    print("Done.")


if __name__ == "__main__":
    main()
