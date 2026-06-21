#!/usr/bin/env python3
"""
Lead-magnet TikTok / YouTube Shorts video engine — one config-driven pipeline
for every vertical's magnet promo.

The image promos cover LinkedIn + Instagram + Facebook. This unlocks the two
highest-reach channels they're dark on: TikTok + YouTube Shorts. Reuses the
proven TikTokReel-Dynamic Remotion composition (kinetic captions, $0 render)
+ the Zernio presign->PUT->create video path.

  python3 magnet_video.py <magnet> --render-only    # render the MP4
  python3 magnet_video.py <magnet> --dry-run        # render + show schedule
  python3 magnet_video.py <magnet> --when ... --schedule-only   # schedule existing MP4
  python3 magnet_video.py <magnet>                  # render + LIVE schedule TikTok + YT

magnets: inner-voices | train-like-a-clinician | marginal-decade | clinic-to-coaching
         (pivot-map shipped via pivot_map_video.py and is already scheduled)

YouTube title MUST go in platformSpecificData.title — a top-level "title" is
silently dropped by Zernio on create (verified Jun 21 2026).
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
load_dotenv(REPO / ".env")

sys.path.insert(0, str(REPO))
from zernio_key import ZERNIO_API_KEY

BASE = "https://zernio.com/api/v1"
HDR = {"Authorization": f"Bearer {ZERNIO_API_KEY}", "Content-Type": "application/json"}
TIMEZONE = "America/New_York"
TIKTOK_ID = "690941425f6fbb9ef8323078"
YOUTUBE_ID = "690940d35f6fbb9ef8323077"

REMOTION_DIR = REPO / "crosswalk-remotion"
COMPOSITION = "TikTokReel-Dynamic"
LINKERO = "linke.ro/crosswalkwisdom"


def seg(text, t, frames):
    return {"text": text, "type": t, "durationFrames": frames}


# ── Magnet config: segments (first-person, grounded in the guide), background,
#    and per-platform copy. One entry per vertical. ────────────────────────────
MAGNETS = {
    "inner-voices": {
        "background": "assets/bg-gen-10-car-rain.jpg",
        "landing": "https://www.crosswalkwisdom.com/inner-voices",
        "youtube_title": "The 5 voices that keep capable people stuck.",
        "segments": [
            seg("I sat in my car for an hour before a shift.", "hook", 52),
            seg("Engine off. Just sitting.", "hook", 42),
            seg("", "pause", 12),
            seg("I told myself I was tired.", "body", 45),
            seg("I wasn't tired.", "body", 40),
            seg("", "pause", 12),
            seg("There's a voice that keeps capable people stuck.", "body", 55),
            seg("It sounds like caution.", "body", 44),
            seg("It sounds responsible.", "body", 44),
            seg("", "pause", 12),
            seg("\"Be realistic. Not yet. You can't afford the risk.\"", "body", 60),
            seg("", "pause", 10),
            seg("That voice isn't lying to hurt you.", "body", 50),
            seg("It's trying to keep you safe.", "body", 46),
            seg("It just never learned the cost of staying.", "body", 55),
            seg("", "pause", 14),
            seg("I named five of them.", "body", 44),
            seg("The Realist. The Loyalist. The Impostor.", "body", 54),
            seg("The Perfectionist. The Martyr.", "body", 48),
            seg("", "pause", 12),
            seg("Once I could name them, I could answer them.", "body", 56),
            seg("", "pause", 18),
            seg("The 5 Inner Voices Keeping You Stuck. Free. Link in bio.", "cta", 80),
        ],
        "tiktok_caption": (
            "If you're capable and still stuck, it's probably not discipline.\n\n"
            "It's a voice that sounds like caution and keeps you exactly where you "
            "are. I named five of them and learned how to answer each one.\n\n"
            "Free guide in bio.\n\n#MentalHealth #Burnout #Identity #SelfSabotage"
        ),
        "youtube_desc": (
            "Most of the time, capable people don't stay stuck from lack of "
            "discipline. They stay stuck because an inner voice that sounds like "
            "caution is doing its job too well. I named five of them, the Realist, "
            "the Loyalist, the Impostor, the Perfectionist, the Martyr, and worked "
            "out how to answer each one.\n\n"
            "Free guide: The 5 Inner Voices Keeping You Stuck.\n"
            "https://www.crosswalkwisdom.com/inner-voices\n\n"
            "#Shorts #MentalHealth #Burnout #Identity"
        ),
        "first_comment": (
            "The free guide names all five voices and how to answer each one: "
            "https://www.crosswalkwisdom.com/inner-voices"
        ),
    },
    "train-like-a-clinician": {
        "background": "assets/bg-gen-03-white-coat.jpg",
        "landing": "https://www.crosswalkwisdom.com/train-like-a-clinician",
        "youtube_title": "Most fitness advice is written to sell you something.",
        "segments": [
            seg("Most fitness advice is written to sell you something.", "hook", 58),
            seg("", "pause", 12),
            seg("Supplement brands fund the studies.", "body", 48),
            seg("Equipment companies write the routines.", "body", 50),
            seg("", "pause", 12),
            seg("I read those same studies as a clinician.", "body", 54),
            seg("Most don't say what the ad says.", "body", 50),
            seg("", "pause", 12),
            seg("Here's what actually builds strength.", "body", 50),
            seg("Not how much you lift today.", "body", 46),
            seg("How systematically you improve over months.", "body", 55),
            seg("", "pause", 12),
            seg("Enough protein. Enough sleep. Enough recovery.", "body", 54),
            seg("The boring numbers nobody sells.", "body", 48),
            seg("", "pause", 12),
            seg("And the line between sore and injured.", "body", 52),
            seg("One is progress. One is a warning.", "body", 50),
            seg("", "pause", 16),
            seg("Train Like a Clinician. Free. Link in bio.", "cta", 76),
        ],
        "tiktok_caption": (
            "Most training advice comes from people selling you a product.\n\n"
            "I read the same research as a clinician. The boring fundamentals win: "
            "progressive overload over months, enough protein and sleep, and knowing "
            "the difference between sore and injured.\n\n"
            "Free, no-nonsense guide in bio.\n\n"
            "#StrengthTraining #Biomechanics #Fitness #InjuryPrevention"
        ),
        "youtube_desc": (
            "Most training advice comes from people selling something. Supplement "
            "brands fund the studies, equipment companies write the routines. I read "
            "the same research as a clinician, and the fundamentals that actually "
            "build strength are the boring ones nobody sells: systematic progressive "
            "overload, enough protein and recovery, and knowing the difference "
            "between sore and injured.\n\n"
            "Free guide: Train Like a Clinician.\n"
            "https://www.crosswalkwisdom.com/train-like-a-clinician\n\n"
            "#Shorts #StrengthTraining #Fitness #Biomechanics"
        ),
        "first_comment": (
            "The free guide lays out what the research actually says about strength, "
            "recovery, and staying injury-free: "
            "https://www.crosswalkwisdom.com/train-like-a-clinician"
        ),
    },
    "marginal-decade": {
        "background": "assets/bg-gen-05-crosswalk-dawn.jpg",
        "landing": "https://www.crosswalkwisdom.com/marginal-decade",
        "youtube_title": "Most people treat their 60s like a waiting room.",
        "segments": [
            seg("Most people treat their 60s like a waiting room.", "hook", 56),
            seg("", "pause", 12),
            seg("They think the body already decided.", "body", 50),
            seg("Built in your 40s. Nothing left to change.", "body", 54),
            seg("", "pause", 12),
            seg("I watched patients prove that wrong.", "body", 50),
            seg("And I watched patients prove it right.", "body", 50),
            seg("", "pause", 12),
            seg("The decade from 60 to 70 decides everything.", "body", 56),
            seg("Whether the last one is vibrant or lost.", "body", 52),
            seg("", "pause", 12),
            seg("You're not fighting aging.", "body", 44),
            seg("You're fighting neglect.", "body", 42),
            seg("", "pause", 12),
            seg("Three things move the needle.", "body", 46),
            seg("Muscle you refuse to lose.", "body", 46),
            seg("A short walk after every meal.", "body", 48),
            seg("Sleep you actually protect.", "body", 46),
            seg("", "pause", 16),
            seg("The Marginal Decade. Free guide. Link in bio.", "cta", 76),
        ],
        "tiktok_caption": (
            "Your 60s are not a waiting room.\n\n"
            "The decade between 60 and 70 decides whether the last one is vibrant or "
            "lost. You're not fighting aging, you're fighting neglect. Muscle, a walk "
            "after meals, and sleep do more than most prescriptions.\n\n"
            "Free guide in bio.\n\n#Health #Prevention #Longevity #MetabolicHealth"
        ),
        "youtube_desc": (
            "Most people treat their 60s like a waiting room and assume the "
            "architecture of their health was set in their 40s. It wasn't. The "
            "decade between 60 and 70 decides whether the last healthy one is vibrant "
            "or lost. You're not fighting aging, you're fighting neglect, and three "
            "things move the needle: keeping muscle, walking after meals, and "
            "protecting sleep.\n\n"
            "Free guide: The Marginal Decade.\n"
            "https://www.crosswalkwisdom.com/marginal-decade\n\n"
            "#Shorts #Health #Prevention #Longevity"
        ),
        "first_comment": (
            "The free guide breaks down the few habits that decide your last healthy "
            "decade: https://www.crosswalkwisdom.com/marginal-decade"
        ),
    },
    "clinic-to-coaching": {
        "background": "assets/bg-gen-15-open-road.jpg",
        "landing": "https://www.crosswalkwisdom.com/clinic-to-coaching",
        "youtube_title": "I left medicine to coach. They called it a step down.",
        "segments": [
            seg("I left medicine to coach.", "hook", 46),
            seg("Everyone called it a step down.", "hook", 50),
            seg("", "pause", 12),
            seg("Here's what they missed.", "body", 42),
            seg("", "pause", 10),
            seg("I spent years learning how bodies actually work.", "body", 56),
            seg("Not the Instagram version.", "body", 44),
            seg("The real one.", "body", 38),
            seg("", "pause", 12),
            seg("Most healthcare coaches make one mistake.", "body", 52),
            seg("They dumb it down until it's useless.", "body", 52),
            seg("", "pause", 12),
            seg("The skill isn't simplifying the science.", "body", 54),
            seg("It's translating it without betraying it.", "body", 56),
            seg("", "pause", 12),
            seg("That's the edge a clinician brings.", "body", 50),
            seg("Nobody else in the gym has it.", "body", 48),
            seg("", "pause", 16),
            seg("From Clinic to Coaching. Free playbook. Link in bio.", "cta", 80),
        ],
        "tiktok_caption": (
            "I left medicine to coach and everyone called it a step down.\n\n"
            "They missed the edge: I know how bodies actually work, not the Instagram "
            "version. The skill isn't dumbing the science down. It's translating it "
            "without betraying it.\n\n"
            "Free playbook in bio.\n\n#PersonalTraining #CareerChange #Coaching #Ottawa"
        ),
        "youtube_desc": (
            "I left clinical medicine to coach, and plenty of people called it a step "
            "down. They missed the advantage. You spent years learning how bodies "
            "actually work, not the Instagram version. The mistake most healthcare "
            "coaches make is dumbing the science down until it's useless. The real "
            "skill is translating it without betraying it, and that's the edge a "
            "clinically-trained coach brings.\n\n"
            "Free playbook: From Clinic to Coaching.\n"
            "https://www.crosswalkwisdom.com/clinic-to-coaching\n\n"
            "#Shorts #PersonalTraining #CareerChange #Coaching"
        ),
        "first_comment": (
            "The free playbook shows how to turn clinical credibility into a practice "
            "clients trust: https://www.crosswalkwisdom.com/clinic-to-coaching"
        ),
    },
}


def out_mp4(magnet: str) -> Path:
    return REMOTION_DIR / "out" / f"magnet-{magnet}.mp4"


def props_file(magnet: str) -> Path:
    return REMOTION_DIR / "out" / f"magnet-{magnet}.props.json"


def total_frames(cfg: dict) -> int:
    return sum(s["durationFrames"] for s in cfg["segments"])


def render(magnet: str, cfg: dict) -> None:
    mp4, pf = out_mp4(magnet), props_file(magnet)
    mp4.parent.mkdir(parents=True, exist_ok=True)
    props = {"segments": cfg["segments"], "background": cfg["background"],
             "handle": "@crosswalkwisdom"}
    pf.write_text(json.dumps(props))
    secs = total_frames(cfg) / 30
    print(f"Rendering {magnet} -> {mp4.name}  ({total_frames(cfg)} frames, {secs:.1f}s)")
    subprocess.run(
        ["npx", "remotion", "render", "src/index.tsx", COMPOSITION, str(mp4), f"--props={pf}"],
        cwd=str(REMOTION_DIR), check=True,
    )
    print(f"  -> {mp4}  ({mp4.stat().st_size // 1024} KB)")


def upload_video(path: Path) -> str:
    r = requests.post(f"{BASE}/media/presign", headers=HDR,
                      json={"filename": path.name, "contentType": "video/mp4",
                            "fileSize": path.stat().st_size}, timeout=30)
    r.raise_for_status()
    d = r.json()
    with open(path, "rb") as f:
        requests.put(d["uploadUrl"], data=f,
                     headers={"Content-Type": "video/mp4"}, timeout=300).raise_for_status()
    return d["publicUrl"]


def build_body(cfg: dict, video_url: str, when: str) -> dict:
    return {
        "content": cfg["tiktok_caption"],
        "mediaItems": [{"url": video_url, "type": "video"}],
        "isDraft": False,
        "scheduledFor": when,
        "timezone": TIMEZONE,
        "platforms": [
            {"platform": "tiktok", "accountId": TIKTOK_ID,
             "customContent": cfg["tiktok_caption"], "scheduledFor": when},
            # title goes in platformSpecificData.title — top-level is dropped.
            {"platform": "youtube", "accountId": YOUTUBE_ID,
             "customContent": cfg["youtube_desc"], "scheduledFor": when,
             "platformSpecificData": {"title": cfg["youtube_title"],
                                      "firstComment": cfg["first_comment"]}},
        ],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("magnet", choices=sorted(MAGNETS), help="which magnet video")
    ap.add_argument("--render-only", action="store_true")
    ap.add_argument("--schedule-only", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--when", required=False, help="scheduledFor ET, e.g. 2026-06-25T16:00:00")
    args = ap.parse_args()

    cfg = MAGNETS[args.magnet]
    mp4 = out_mp4(args.magnet)

    if not args.schedule_only:
        render(args.magnet, cfg)
    if args.render_only:
        print("\nRender complete. Preview, then --dry-run to check the schedule.")
        return

    if not mp4.exists():
        sys.exit(f"MP4 missing: {mp4}")

    if args.dry_run:
        print(f"\nDRY RUN — {args.magnet}: would schedule TikTok + YouTube for {args.when}")
        print(f"  video: {mp4.name} ({mp4.stat().st_size // 1024} KB)")
        print(f"  YouTube title: {cfg['youtube_title']}")
        print(f"  first comment: {cfg['first_comment']}")
        print(f"  TikTok link path: bio ({LINKERO})")
        return

    if not args.when:
        sys.exit("--when is required for a live schedule")

    print(f"\nUploading {args.magnet} video...")
    video_url = upload_video(mp4)
    print(f"  -> {video_url}")
    r = requests.post(f"{BASE}/posts", headers=HDR,
                      json=build_body(cfg, video_url, args.when), timeout=60)
    print("HTTP", r.status_code)
    post = r.json().get("post", r.json())
    print(f"  post _id: {post.get('_id')}  status: {post.get('status')}  when: {post.get('scheduledFor')}")
    print(f"  platforms: {[p.get('platform') for p in post.get('platforms', [])]}")


if __name__ == "__main__":
    main()
