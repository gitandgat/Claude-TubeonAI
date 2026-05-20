"""
DALL-E-3 image generation for health/wellness social posts.
Uses the OpenAI image generation API with dall-e-3 model for cost-effective quality.
"""
import os, time, requests
from openai import OpenAI

_client = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    return _client


def generate_health_image(title: str, save_dir: str = "/tmp") -> str:
    """
    Generate a health/wellness image for the given video title.
    If DALL-E is unavailable, generate a simple placeholder image.
    """
    prompt = (
        f"A professional, cinematic health and wellness photograph inspired by the topic: '{title}'. "
        "Style: warm natural light, calm and aspirational mood, clean composition. "
        "No text overlays, no logos. Suitable for a LinkedIn post. "
        "Examples: person meditating in sunlight, fresh vegetables on marble, "
        "someone running in nature, a serene workspace, balanced lifestyle imagery."
    )

    client = _get_client()

    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        img_url = response.data[0].url
        img_data = requests.get(img_url, timeout=30).content

        filename = f"health_post_{int(time.time())}.png"
        path = os.path.join(save_dir, filename)
        with open(path, "wb") as f:
            f.write(img_data)

        return path
    except Exception as e:
        pass

    # If all models fail, generate a simple placeholder image
    from PIL import Image, ImageDraw

    img = Image.new("RGB", (1024, 1024), color=(240, 245, 250))
    draw = ImageDraw.Draw(img)

    # Add simple design: gradient-like background
    for i in range(1024):
        color_intensity = int(240 + (20 * i / 1024))
        draw.line([(0, i), (1024, i)], fill=(color_intensity - 20, color_intensity, color_intensity))

    filename = f"health_post_{int(time.time())}.png"
    path = os.path.join(save_dir, filename)
    img.save(path)

    return path
