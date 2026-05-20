"""
Crosswalk Wisdom — Story Asset Generator
Generates background images for "The Morning Nobody Knew My Name" story.
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

ASSETS = [
    # ── Scene 1: The cold Canadian morning — shaking hands moment ────────────
    {
        "filename": "bg-story-winter-crosswalk.jpg",
        "aspect_ratio": "social_story_9_16",
        "prompt": (
            "Cinematic 35mm film photograph of a Canadian urban crosswalk at dawn in deep winter. "
            "-8 degrees celsius atmosphere, frost on the asphalt, visible breath in cold air. "
            "A lone orange-vested figure stands at the crossing, stop sign held low. "
            "Bare trees, grey-blue sky just beginning to lighten at the horizon. "
            "Blue-cold ambient light, warm amber street lamps still on. "
            "Film grain, melancholic yet peaceful. Vertical 9:16 composition. "
            "Sense of stillness, isolation, transformation. No cars. "
            "Empty street, white crosswalk stripes, stop sign in frame."
        ),
    },
    # ── Scene 4: The turn — small child's hand reaching up to adult's hand ───
    {
        "filename": "bg-story-child-hand.jpg",
        "aspect_ratio": "social_story_9_16",
        "prompt": (
            "Cinematic 35mm film photograph of a small child's hand reaching up to hold "
            "an adult's gloved hand at a pedestrian crossing. "
            "Child's hand tiny and soft, adult's hand larger, gentle grip. "
            "Warm amber morning light falling on the hands from the side. "
            "Urban crosswalk stripes visible on the ground below, softly blurred. "
            "Intimate, emotional, symbolic of trust and connection. "
            "Shallow depth of field, hands in sharp focus, background soft. "
            "Film grain, warm charcoal tones. Vertical 9:16 composition. "
            "No faces visible — the hands are the entire story."
        ),
    },
    # ── Scene 5: Return to Thailand — warmth, transformation, arrival ─────────
    {
        "filename": "bg-story-thailand-return.jpg",
        "aspect_ratio": "social_story_9_16",
        "prompt": (
            "Cinematic 35mm film photograph of a warm tropical pedestrian crossing in Thailand. "
            "Late afternoon golden hour light, amber and honey tones flooding the scene. "
            "Lush green trees on either side of a wide boulevard crosswalk. "
            "A lone middle-aged Asian man walks toward the camera across the stripes, "
            "calm, unhurried, at peace. Slight smile visible. "
            "Warm humid atmosphere, soft tropical bokeh, vibrant yet grounded. "
            "Film grain, rich warm palette contrasting with cold Canadian blue tones. "
            "Vertical 9:16 composition. Sense of homecoming and transformation."
        ),
    },
    # ── Square version of child's hand for Instagram feed ────────────────────
    {
        "filename": "bg-story-child-hand-square.jpg",
        "aspect_ratio": "square_1_1",
        "prompt": (
            "Cinematic 35mm film close-up photograph of a small child's hand reaching up "
            "to hold an adult's gloved hand at a pedestrian crosswalk. "
            "Warm amber morning light from the side. "
            "Urban crosswalk stripes softly visible below, out of focus. "
            "Intimate, emotional, trust and connection. "
            "Film grain, warm charcoal tones. Square 1:1 composition. "
            "Shallow depth of field. No faces. The hands tell the whole story."
        ),
    },
    # ── Square: winter crosswalk for Instagram feed ──────────────────────────
    {
        "filename": "bg-story-winter-crosswalk-square.jpg",
        "aspect_ratio": "square_1_1",
        "prompt": (
            "Cinematic 35mm film photograph of a Canadian pedestrian crosswalk in deep winter. "
            "Frost on asphalt, -8 degree celsius atmosphere. "
            "Blue-cold ambient light, amber street lamp glow on the left. "
            "Empty street, white crosswalk stripes leading into frame. "
            "Stop sign visible on the right edge. No people. "
            "Film grain, cold blue palette with warm amber accents. "
            "Square 1:1 composition. Isolation, stillness, brave solitude."
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
    print("  Crosswalk Wisdom — Story Asset Generator")
    print("  Story: 'The Morning Nobody Knew My Name'")
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
