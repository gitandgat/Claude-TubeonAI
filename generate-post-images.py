"""
Generate 8 square (1:1) Freepik images for Crosswalk Wisdom LinkedIn/Instagram/Facebook posts.
Uses Freepik Mystic async API.
"""

import requests
import time
import os

API_KEY = "***REMOVED-FREEPIK-KEY***"
BASE = "https://api.freepik.com/v1/ai/mystic"
HEADERS = {
    "x-freepik-api-key": API_KEY,
    "Content-Type": "application/json",
}
OUT_DIR = "/Users/toto/Claude TubeonAI/crosswalk-remotion/public/assets"

BRAND_STYLE = "35mm film grain, warm amber golden tones, cinematic lighting, shallow depth of field, moody atmosphere, professional photography"

IMAGES = [
    {
        "filename": "post-sunk-cost.jpg",
        "prompt": f"Empty hospital corridor at night with warm amber light streaming through a window at the far end, long shadows on polished floor, stethoscope abandoned on a bench, {BRAND_STYLE}",
    },
    {
        "filename": "post-what-will-people-think.jpg",
        "prompt": f"Silhouette of a person standing at a large window looking out at a city at dawn, warm golden light on their face, contemplative mood, back turned to viewer, {BRAND_STYLE}",
    },
    {
        "filename": "post-quitting-is-not-failure.jpg",
        "prompt": f"A fork in a road at golden hour sunrise, one path leading into fog and one into warm light, trees lining both sides, dramatic sky, {BRAND_STYLE}",
    },
    {
        "filename": "post-fear-audit-intro.jpg",
        "prompt": f"Person walking alone through morning fog on a crosswalk, amber street lights glowing, urban setting, seen from behind, determination in posture, {BRAND_STYLE}",
    },
    {
        "filename": "post-naming-fear.jpg",
        "prompt": f"Kitchen table with a single piece of paper and pen, warm morning light streaming through window, coffee cup, intimate close-up, peaceful stillness, {BRAND_STYLE}",
    },
    {
        "filename": "post-five-fears.jpg",
        "prompt": f"Five closed wooden doors in a dimly lit hallway, each door illuminated by a different shade of warm amber light from behind, mysterious atmosphere, {BRAND_STYLE}",
    },
    {
        "filename": "post-four-stages.jpg",
        "prompt": f"Four stepping stones across still water at dawn, each stone progressively more illuminated by golden sunrise light, mist rising from water, {BRAND_STYLE}",
    },
    {
        "filename": "post-why-i-built-it.jpg",
        "prompt": f"Close-up of hands writing on paper with a pen at a wooden table, warm amber light from a nearby window, journal pages visible, emotional intimacy, {BRAND_STYLE}",
    },
]


def generate_image(prompt):
    """Submit generation task and poll until complete."""
    payload = {
        "prompt": prompt,
        "image": {"size": "square_1_1"},
    }
    resp = requests.post(BASE, headers=HEADERS, json=payload)
    resp.raise_for_status()
    data = resp.json()

    task_id = data.get("data", {}).get("task_id")
    if not task_id:
        # Synchronous response
        generated = data.get("data", {}).get("generated", [])
        if generated:
            return generated[0]
        raise ValueError(f"No task_id or generated data: {data}")

    # Poll for completion
    poll_url = f"{BASE}/{task_id}"
    for attempt in range(60):
        time.sleep(3)
        poll_resp = requests.get(poll_url, headers=HEADERS)
        poll_resp.raise_for_status()
        poll_data = poll_resp.json()
        status = poll_data.get("data", {}).get("status")
        if status == "COMPLETED":
            generated = poll_data.get("data", {}).get("generated", [])
            if generated:
                return generated[0]
            raise ValueError(f"Completed but no generated data: {poll_data}")
        elif status in ("FAILED", "ERROR"):
            raise ValueError(f"Task failed: {poll_data}")
        print(f"  Polling {task_id}... ({status})")

    raise TimeoutError(f"Task {task_id} did not complete in time")


def download_image(url, filepath):
    resp = requests.get(url, timeout=120)
    resp.raise_for_status()
    with open(filepath, "wb") as f:
        f.write(resp.content)
    size_mb = os.path.getsize(filepath) / (1024 * 1024)
    return size_mb


if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    print(f"Generating {len(IMAGES)} images...\n")

    for i, img in enumerate(IMAGES, 1):
        filepath = os.path.join(OUT_DIR, img["filename"])
        print(f"[{i}/{len(IMAGES)}] {img['filename']}")
        try:
            result = generate_image(img["prompt"])
            # result is a URL string
            url = result if isinstance(result, str) else result.get("url", result)
            size = download_image(url, filepath)
            print(f"  OK — {size:.1f} MB")
        except Exception as e:
            print(f"  FAILED: {e}")

    print("\nDone.")
