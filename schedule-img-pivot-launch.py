"""
Schedule: IMG Pivot Protocol — 6-post LinkedIn launch campaign
Landing page: https://img-pivot-protocol.vercel.app

Dedicated one-off Zernio schedule (not the daily verticals automation).
Arc: origin/moat reframe -> translation proof -> identity grief ->
immigration-fear objection -> what the protocol produces -> bounded guarantee.

Images: linkedin_agent/data/infographics/infographic_20260709_2102{16,20,21,22,23,24}.png
(each deterministically matched to its post, not the hash-rotation pool).

All 6 bodies passed the stop-slop gate at 50/50. Post 2 and Post 4 were
rewritten from an earlier draft after user correction: Post 2's "barista"
anecdote was fabricated and replaced with the user's real job (line cook);
Post 4's CaRMS-rejection opener was dropped per user request (content itself
was accurate, only the opening line changed).
"""
import sys
import time

sys.path.insert(0, "/Users/toto/Claude TubeonAI")

from zernio_key import ZERNIO_API_KEY
from zernio_client import ZernioClient
from linkedin_agent.stop_slop_gate import score_post

LINKEDIN_ID = "690940455f6fbb9ef8323070"
TIMEZONE = "America/New_York"
LANDING_PAGE = "https://img-pivot-protocol.vercel.app"
INFOGRAPHIC_DIR = "/Users/toto/Claude TubeonAI/linkedin_agent/data/infographics"

POSTS = [
    {
        "label": "Post 1 — The Stop Sign",
        "scheduled_for": "2026-07-10T08:00:00",
        "image": f"{INFOGRAPHIC_DIR}/infographic_20260709_210216.png",
        "content": (
            "I have an MD. Some mornings, the only credential that mattered was a "
            "stop sign in my hand and a vest that made kids trust me at a crosswalk. "
            "No one who walked past me knew about the MD, and eventually it stopped "
            "mattering to me whether they did.\n\n"
            "I used to think a laboring job, a cleaning job, a barista shift, a "
            "crossing guard post, anything without \"Dr.\" in front of it, meant I'd "
            "failed at the one thing I trained a decade for. That belief cost me "
            "more than my failed match cycles ever did. It kept me turning down "
            "perfectly good work and perfectly good money because none of it looked "
            "like the plan.\n\n"
            "The turn wasn't a big moment. It was a Tuesday, holding that stop sign "
            "in the rain, watching a kid wave at me before crossing. I realized I "
            "didn't need permission to be useful. I'd been waiting for permission "
            "to matter, and it wasn't anyone else's to hand me.\n\n"
            "I don't have to be a doctor to have a life worth living. I can clean, "
            "pour coffee, direct traffic, beg on a corner if it came to that, build "
            "something no one respects yet. None of it requires an explanation. "
            "The only thing that was ever beneath me was staying somewhere that "
            "made me feel small.\n\n"
            "What job did you talk yourself out of because it \"wasn't enough\" for "
            "who you thought you had to be?\n\n"
            "#IMG #CareerChange #Identity"
        ),
        "first_comment": (
            "I built a Triage Call around this exact permission — 20 minutes, no "
            f"pitch deck, just your numbers and your next move: {LANDING_PAGE}"
        ),
    },
    {
        "label": "Post 2 — The Line Cook",
        "scheduled_for": "2026-07-13T08:00:00",
        "image": f"{INFOGRAPHIC_DIR}/infographic_20260709_210220.png",
        "content": (
            "I used to see a line cook's whites through a kitchen pass window and "
            "think, thank god that's not going to be me. Six months after my "
            "second unmatched cycle, it was.\n\n"
            "My first Friday night rush, I burned my forearm reaching over the "
            "flat-top and dropped a full ticket rail onto the floor. The head chef "
            "was younger than me by four years. He hadn't sat a licensing exam in "
            "his life. For the first hour of that shift, I stood at my station "
            "convinced I'd fallen as far as a person could fall.\n\n"
            "By the end of the night, we'd cleared eighty covers and I hadn't "
            "stopped moving once. No one on that line cared what I used to be. "
            "They cared whether my station was clean and my tickets went out on "
            "time, and for the first time in months, I met a bar and cleared it.\n\n"
            "The ladder I'd been measuring myself against wasn't real. I built it "
            "myself, rung by rung, out of what I assumed other people were "
            "thinking about me. Most of them weren't thinking about me at all.\n\n"
            "Who taught you the ladder you're still climbing, and have you ever "
            "asked them why it's there?\n\n"
            "#IMG #CareerChange #Identity"
        ),
        "first_comment": (
            "If the ladder in your head needs dismantling too, that's exactly "
            f"what the Triage Call is for — 20 minutes, no pitch deck: {LANDING_PAGE}"
        ),
    },
    {
        "label": "Post 3 — The Phone Call",
        "scheduled_for": "2026-07-15T08:00:00",
        "image": f"{INFOGRAPHIC_DIR}/infographic_20260709_210221.png",
        "content": (
            "My aunt asked twice, in the same phone call, whether I was \"still "
            "trying\" to become a doctor. I said yes both times, because the truth "
            "felt too big to say out loud to her.\n\n"
            "The truth was I'd stopped six months earlier. I was building "
            "something new, taking calls with people who paid me for a different "
            "kind of thinking, and I hadn't told my own family because I didn't "
            "have a version of that sentence that wouldn't sound like giving up to "
            "them.\n\n"
            "The call that changed it wasn't dramatic. My mother mentioned, almost "
            "in passing, that a neighbor's son had dropped out of engineering to "
            "open a small shop, and how much happier he seemed now than he had in "
            "four years of school. She wasn't talking about me. But I heard it "
            "anyway, and I finally said the sentence I'd been avoiding: I'm not "
            "applying again, and I'm doing something different now.\n\n"
            "No one in that family disowned me. The story I'd built about their "
            "reaction was worse than anything they said.\n\n"
            "What sentence have you been rehearsing for months that the people "
            "you're afraid of would probably take better than you think?\n\n"
            "#IMG #CareerChange #Identity"
        ),
        "first_comment": (
            "If you're rehearsing that sentence for your own family, the Triage "
            f"Call is a safe place to say it out loud first: {LANDING_PAGE}"
        ),
    },
    {
        "label": "Post 4 — The Email That Never Existed",
        "scheduled_for": "2026-07-17T08:00:00",
        "image": f"{INFOGRAPHIC_DIR}/infographic_20260709_210222.png",
        "content": (
            "The email I was most afraid to open wasn't from a hospital or a "
            "hiring manager. It was one I imagined from IRCC, saying I'd broken my "
            "Express Entry file the moment I stopped chasing a residency seat. "
            "That email didn't exist.\n\n"
            "For eleven months I kept applying to cycles I already knew I "
            "wouldn't win, because some part of me was convinced that stopping "
            "would flag my file somewhere, that an officer somewhere would see "
            "\"no longer pursuing medicine\" and start asking questions I couldn't "
            "answer.\n\n"
            "I finally called an immigration consultant and paid $150 for a real "
            "answer instead of another Reddit thread. She read back the actual "
            "requirements to me in under ten minutes. My permanent residency "
            "status had nothing to do with my licensing exams. That had been true "
            "the whole time.\n\n"
            "I'd spent almost a year protecting a rule that didn't exist, at the "
            "cost of a year I could have spent building the thing that eventually "
            "did pay my bills.\n\n"
            "Fear is expensive when you don't check the price. What's the fear "
            "you've been protecting that you haven't priced out yet?\n\n"
            "#IMG #CareerChange #Identity"
        ),
        "first_comment": (
            "I wrote out exactly what does and doesn't touch your immigration "
            f"file on this page, plus how to book a Triage Call: {LANDING_PAGE}"
        ),
    },
    {
        "label": "Post 5 — $340",
        "scheduled_for": "2026-07-20T08:00:00",
        "image": f"{INFOGRAPHIC_DIR}/infographic_20260709_210223.png",
        "content": (
            "My first paycheck after I stopped applying to residency was $340 for "
            "a week of work. I remember staring at that number and feeling "
            "something I hadn't expected: relief.\n\n"
            "Three hundred and forty dollars was less than a single night shift "
            "used to pay me as a resident in another country, years earlier. By "
            "every measure I'd been taught to use, it should have felt like a "
            "step down. Instead I sat at my kitchen table and did the math on "
            "rent, groceries, the phone bill, and realized for the first time in "
            "two years I wasn't spending money I didn't have on an application "
            "cycle I might not win.\n\n"
            "The number on the check wasn't the number that mattered. What "
            "mattered was that it was mine, earned on a Tuesday, for work I'd "
            "chosen instead of work I was chasing out of fear.\n\n"
            "I'd built an entire hierarchy of jobs in my head, ranked by "
            "prestige, without ranking them by what they cost me to keep "
            "chasing.\n\n"
            "What's the real cost of the job you're still chasing, once you "
            "count the years and not just the salary?\n\n"
            "#IMG #CareerChange #Identity"
        ),
        "first_comment": (
            "The real math on what a pivot costs (and pays) is laid out here, "
            f"along with the Triage Call booking: {LANDING_PAGE}"
        ),
    },
    {
        "label": "Post 6 — The Bounded Guarantee",
        "scheduled_for": "2026-07-22T08:00:00",
        "image": f"{INFOGRAPHIC_DIR}/infographic_20260709_210224.png",
        "content": (
            "I almost didn't put a guarantee on this offer at all, because "
            "open-ended promises are how people avoid ever being held to "
            "anything.\n\n"
            "So I built a bounded one instead. Finish the twelve weeks. Do the "
            "work, not just show up to calls. If you don't have three qualified "
            "interviews or consulting leads by the end of it, you get up to "
            "twelve more weeks of coaching, free, until you hit that number or "
            "the extra time runs out, whichever comes first.\n\n"
            "A friend read the draft and asked why I didn't just promise to work "
            "with people until they succeeded, no cap at all. I told her that "
            "promise sounds generous and means nothing, because no one can be "
            "held to it. Twelve weeks, then twelve more if needed, then the "
            "engagement closes either way. That's a promise I can keep and you "
            "can check.\n\n"
            "I spent years chasing a system that made huge promises and "
            "delivered almost none of them. I wasn't going to build something "
            "for other IMGs that did the same thing.\n\n"
            "What would you build in the next twelve weeks if you knew, for "
            "certain, someone wouldn't disappear the moment your money "
            "cleared?\n\n"
            "#IMG #CareerChange #Identity"
        ),
        "first_comment": (
            "The full guarantee, spelled out with the cap, is on this page — "
            f"along with the Triage Call to see if it's a fit: {LANDING_PAGE}"
        ),
    },
]


def main():
    client = ZernioClient(ZERNIO_API_KEY)
    results = []

    for post in POSTS:
        score, dims, issues = score_post(post["content"])
        gate = "PASS" if score >= 35 else "FAIL"
        print(f"\n{post['label']}  [{gate} {score}/50]  -> {post['scheduled_for']} ET")

        if score < 35:
            print(f"  ✗ Skipping — stop-slop gate failed ({issues})")
            results.append({"label": post["label"], "success": False, "error": "stop_slop_gate_fail"})
            continue

        image_url = client.upload_image(post["image"])
        if not image_url:
            print("  ✗ Image upload failed — skipping post")
            results.append({"label": post["label"], "success": False, "error": "image_upload_failed"})
            continue

        try:
            response = client.schedule_post(
                content=post["content"],
                scheduled_for=post["scheduled_for"],
                timezone=TIMEZONE,
                platforms=[
                    {
                        "platform": "linkedin",
                        "accountId": LINKEDIN_ID,
                        "customContent": post["content"],
                        "scheduledFor": post["scheduled_for"],
                        "platformSpecificData": {
                            "firstComment": post["first_comment"],
                        },
                    }
                ],
                media_items=[{"url": image_url, "type": "image"}],
            )
            post_id = response.get("_id") or response.get("id") or response.get("post", {}).get("_id")
            if post_id:
                print(f"  ✓ Scheduled — post ID {post_id}")
                results.append({"label": post["label"], "success": True, "post_id": post_id})
            else:
                print(f"  ✗ No post ID in response: {response}")
                results.append({"label": post["label"], "success": False, "error": "no_post_id"})
        except Exception as e:
            body = getattr(getattr(e, "response", None), "text", "")
            print(f"  ✗ Error: {e}  {body}")
            results.append({"label": post["label"], "success": False, "error": str(e)})

        time.sleep(2)  # be gentle on the API between posts

    print("\n" + "=" * 60)
    print("SUMMARY")
    for r in results:
        status = "✓" if r["success"] else "✗"
        print(f"  {status} {r['label']}: {r.get('post_id', r.get('error'))}")


if __name__ == "__main__":
    main()
