"""
Crosswalk Wisdom — Freepik Asset Generator
Generates background images for all Remotion compositions.
"""

import base64
import json
import time
import requests
from pathlib import Path

FREEPIK_KEY = "FPSX177e77844980578ef13326e9b9f8ad7d"
API_URL = "https://api.freepik.com/v1/ai/mystic"
OUTPUT = Path("./crosswalk-remotion/public/assets")
OUTPUT.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "x-freepik-api-key": FREEPIK_KEY,
    "Content-Type": "application/json",
    "Accept": "application/json",
}

# Brand palette for prompt injection
BRAND = (
    "warm amber golden tones, deep charcoal background, cinematic 35mm film grain, "
    "urban crosswalk setting, atmospheric, slightly desaturated, editorial photography"
)

ASSETS = [
    # ── Instagram Carousel Backgrounds (square 1:1) ──────────────────────────
    {
        "filename": "bg-carousel-md-to-crossing-guard.jpg",
        "aspect_ratio": "square_1_1",
        "prompt": (
            "Cinematic 35mm film photograph of an empty Canadian urban crosswalk at sunrise. "
            "Red octagonal stop sign in background softly blurred. "
            "White pedestrian crossing stripes on dark wet asphalt. "
            "Warm amber golden light raking across the scene. "
            "Deep charcoal shadows, soft film grain, melancholic hopeful mood. "
            "No people. Wide establishing shot. Atmospheric haze."
        ),
    },
    {
        "filename": "bg-carousel-not-your-job-title.jpg",
        "aspect_ratio": "square_1_1",
        "prompt": (
            "Cinematic close-up 35mm film photograph of a yellow reflective crossing guard vest "
            "hanging on a hook or draped over a railing. "
            "Warm amber bokeh background of an urban street at dusk. "
            "Deep charcoal tones, film grain, moody and intimate. "
            "Identity and transformation concept. "
            "Shallow depth of field, soft focus background."
        ),
    },
    {
        "filename": "bg-carousel-nobody-tells-you.jpg",
        "aspect_ratio": "square_1_1",
        "prompt": (
            "Cinematic 35mm film photograph of a lone crossing guard standing at an empty "
            "intersection just before dawn. "
            "Silhouette against soft amber street lights. "
            "Quiet, peaceful, reflective atmosphere. "
            "Urban Canadian street, light mist, film grain. "
            "Wide shot, crossing stripes visible, stop sign in distance. "
            "Freedom and solitude mood."
        ),
    },

    # ── TikTok / Reel Backgrounds (vertical 9:16) ────────────────────────────
    {
        "filename": "bg-tiktok-pov-doctor-crossing-guard.jpg",
        "aspect_ratio": "social_story_9_16",
        "prompt": (
            "Cinematic portrait 35mm film photograph of a middle-aged Asian man in a bright "
            "yellow reflective crossing guard vest, holding a stop sign paddle. "
            "Warm morning amber light. Soft smile, calm eyes, sense of peace. "
            "Urban Canadian street background, softly blurred. "
            "Film grain, authentic documentary style. "
            "Vertical composition, subject centered, space at top for text overlay."
        ),
    },
    {
        "filename": "bg-tiktok-psychiatrist-story.jpg",
        "aspect_ratio": "social_story_9_16",
        "prompt": (
            "Cinematic portrait 35mm film photograph of a crosswalk in a quiet Canadian "
            "residential neighbourhood at golden hour. "
            "Warm amber sunlight streaming between buildings. "
            "Empty street, white crossing stripes, stop sign visible. "
            "Contemplative, peaceful, transitional mood. "
            "Vertical composition, film grain, desaturated warm palette."
        ),
    },
    {
        "filename": "bg-tiktok-things-people-say.jpg",
        "aspect_ratio": "social_story_9_16",
        "prompt": (
            "Cinematic 35mm film portrait of a middle-aged Asian crossing guard in yellow vest "
            "and reflective gear, arms slightly open, confident relaxed posture. "
            "Urban street background, warm amber bokeh. "
            "Film grain, authentic, documentary feel. "
            "Vertical composition. Space at top and bottom for text overlay captions."
        ),
    },
    {
        "filename": "bg-tiktok-yellow-vest.jpg",
        "aspect_ratio": "social_story_9_16",
        "prompt": (
            "Cinematic 35mm film close-up photograph of a bright yellow safety vest with "
            "reflective silver stripes, slightly worn, authentic. "
            "Draped casually over something, urban crosswalk visible softly blurred behind. "
            "Warm amber street light glow. "
            "Film grain, intimate, symbolic composition. "
            "Vertical format."
        ),
    },

    # ── LinkedIn Video Backgrounds (landscape 16:9) ──────────────────────────
    {
        "filename": "bg-linkedin-sunk-cost.jpg",
        "aspect_ratio": "widescreen_16_9",
        "prompt": (
            "Cinematic wide 35mm film photograph of a long empty hospital corridor at night. "
            "Fluorescent ceiling lights receding into the distance, slightly overexposed. "
            "Cold institutional blue-white light contrasting with warm amber exit sign glow. "
            "Moody, isolating, contemplative. "
            "Film grain, slightly blurred, abstract. "
            "Wide landscape format."
        ),
    },
    {
        "filename": "bg-linkedin-what-will-people-think.jpg",
        "aspect_ratio": "widescreen_16_9",
        "prompt": (
            "Cinematic wide 35mm film photograph of an empty urban intersection at dawn. "
            "Multiple pedestrian crossing stripes converging. "
            "Soft amber golden light from the horizon. "
            "Mist in the air, quiet city, no people, no cars. "
            "Contemplative, open, full of possibility. "
            "Film grain. Wide landscape format."
        ),
    },
    {
        "filename": "bg-linkedin-quitting-is-not-failure.jpg",
        "aspect_ratio": "widescreen_16_9",
        "prompt": (
            "Cinematic wide 35mm film photograph of a fork in an urban road at sunrise. "
            "One path leads towards a bright amber light on the horizon. "
            "The other path recedes into shadow. "
            "Crosswalk stripes visible. Warm hopeful mood. "
            "Film grain. Wide landscape format. No people."
        ),
    },
    {
        "filename": "bg-linkedin-fear-audit-intro.jpg",
        "aspect_ratio": "widescreen_16_9",
        "prompt": (
            "Cinematic wide 35mm film photograph of a middle-aged Asian man in a yellow "
            "crossing guard vest standing at a crosswalk, seen from behind, "
            "looking out at a wide empty city street at sunrise. "
            "Amber golden light flooding the scene. "
            "Peaceful, reflective, full of possibility. "
            "Film grain. Wide landscape format."
        ),
    },

    # ── Quiz Result Backgrounds (shared) ─────────────────────────────────────
    {
        "filename": "bg-quiz-result-neutral.jpg",
        "aspect_ratio": "square_1_1",
        "prompt": (
            "Cinematic 35mm film photograph of a crosswalk at dawn. "
            "White stripes on dark asphalt, leading towards amber light. "
            "Hopeful, transitional, symbolic of new beginnings. "
            "Film grain, warm charcoal palette. No people. "
            "Square composition."
        ),
    },
]


def generate(asset: dict) -> bool:
    payload = {
        "prompt": asset["prompt"],
        "aspect_ratio": asset["aspect_ratio"],
        "num_images": 1,
        "image_format": "jpg",
        "quality": 80,
        "safety_tolerance": 2,
    }

    try:
        resp = requests.post(API_URL, headers=HEADERS, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        if "invalid_params" in data:
            print(f"  ✗  Validation error: {data['invalid_params']}")
            return False

        task_id = data["data"]["task_id"]
        print(f"       task_id={task_id} — polling…", end="", flush=True)

        poll_url = f"{API_URL}/{task_id}"
        for _ in range(90):
            time.sleep(2)
            poll = requests.get(poll_url, headers=HEADERS, timeout=30)
            poll.raise_for_status()
            result = poll.json()
            status = result["data"].get("status", "")
            if status == "COMPLETED":
                break
            if status in ("FAILED", "ERROR", "failed", "error"):
                print(f"\n  ✗  Task failed: {result}")
                return False
            print(".", end="", flush=True)
        else:
            print("\n  ✗  Timed out")
            return False

        print()
        generated = result["data"].get("generated", [])
        if not generated:
            print(f"  ✗  No images returned: {result['data']}")
            return False

        img_data = generated[0]
        # Mystic may return a URL string directly, or a dict with base64/url
        if isinstance(img_data, str):
            img_resp = requests.get(img_data, timeout=60)
            img_resp.raise_for_status()
            img_bytes = img_resp.content
        elif isinstance(img_data, dict):
            if "base64" in img_data:
                img_bytes = base64.b64decode(img_data["base64"])
            elif "url" in img_data:
                img_resp = requests.get(img_data["url"], timeout=60)
                img_resp.raise_for_status()
                img_bytes = img_resp.content
            else:
                print(f"  ✗  Unknown image format: {list(img_data.keys())}")
                return False
        else:
            print(f"  ✗  Unexpected type: {type(img_data)}")
            return False

        out_path = OUTPUT / asset["filename"]
        out_path.write_bytes(img_bytes)
        print(f"  ✓  Saved → {out_path}")
        return True

    except requests.HTTPError as e:
        print(f"  ✗  HTTP {e.response.status_code}: {e.response.text[:300]}")
        return False
    except Exception as e:
        print(f"  ✗  Error: {e}")
        return False


if __name__ == "__main__":
    print(f"\n{'='*60}")
    print("  Crosswalk Wisdom — Freepik Asset Generator")
    print(f"  Output: {OUTPUT.resolve()}")
    print(f"  Total:  {len(ASSETS)} assets")
    print(f"{'='*60}\n")

    success, failed = [], []

    for i, asset in enumerate(ASSETS, 1):
        print(f"[{i:02d}/{len(ASSETS)}] {asset['filename']}")
        ok = generate(asset)
        (success if ok else failed).append(asset["filename"])
        if i < len(ASSETS):
            time.sleep(1)

    print(f"\n{'='*60}")
    print(f"  Done — {len(success)}/{len(ASSETS)} generated.")
    if failed:
        print(f"  Failed: {', '.join(failed)}")
    print(f"  Assets at: {OUTPUT.resolve()}")
    print(f"{'='*60}\n")

    manifest = [{"filename": a["filename"], "aspect_ratio": a["aspect_ratio"]} for a in ASSETS]
    (OUTPUT / "manifest.json").write_text(json.dumps(manifest, indent=2))
    print("  manifest.json saved.\n")
