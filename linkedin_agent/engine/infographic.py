import os
import subprocess
from datetime import datetime

# Add parent directories to path for imports
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from linkedin_agent.config import INFOGRAPHIC_WIDTH, INFOGRAPHIC_HEIGHT, DATA_DIR

_REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_ASSETS = os.path.join(_REPO, "crosswalk-remotion", "public", "assets")

# Curated cinematic backgrounds (reuse the same shots the videos use). Rotated
# per post so a batch of 5 doesn't repeat the same image.
BACKGROUNDS = [
    "bg-linkedin-sunk-cost.jpg",
    "bg-linkedin-quitting-is-not-failure.jpg",
    "bg-linkedin-what-will-people-think.jpg",
    "bg-linkedin-fear-audit-intro.jpg",
    "bg-tiktok-yellow-vest.jpg",
    "bg-tiktok-pov-doctor-crossing-guard.jpg",
    "bg-tiktok-psychiatrist-story.jpg",
    "bg-story-winter-crosswalk-square.jpg",
    "bg-story-child-hand-square.jpg",
]


class InfographicEngine:
    def __init__(self):
        self.width = INFOGRAPHIC_WIDTH
        self.height = INFOGRAPHIC_HEIGHT
        self.output_dir = f"{DATA_DIR}/infographics"
        os.makedirs(self.output_dir, exist_ok=True)

    def _pick_background(self, seed: str) -> str:
        """Absolute file path to a background, chosen deterministically per hook.

        Pool = the curated set PLUS any bulk-generated images named bg-gen-*.jpg
        dropped into the assets folder (auto-discovered — no code edit needed).
        """
        import glob
        existing = [os.path.join(_ASSETS, b) for b in BACKGROUNDS
                    if os.path.exists(os.path.join(_ASSETS, b))]
        existing += sorted(glob.glob(os.path.join(_ASSETS, "bg-gen-*.jpg")))
        existing += sorted(glob.glob(os.path.join(_ASSETS, "bg-gen-*.png")))
        if not existing:
            return ""
        return existing[hash(seed) % len(existing)]

    def generate_html_template(self, hook: str, background_path: str) -> str:
        """Generate HTML: cinematic photo background + dark gradient + brand text."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        html_file = f"{self.output_dir}/infographic_{timestamp}.html"

        # file:// URL so shot-scraper (a local browser) can load the image
        bg_url = "file://" + background_path if background_path else ""
        bg_layer = (f"background-image: url('{bg_url}'); background-size: cover; "
                    f"background-position: center;") if bg_url else \
                   "background: linear-gradient(135deg, #2C2C2C 0%, #1a1a1a 100%);"

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;800&family=Inter:wght@400;600&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ width: {self.width}px; height: {self.height}px; overflow: hidden; }}
        .stage {{ position: relative; width: 100%; height: 100%; {bg_layer} }}
        /* Dark gradient — light at top, heavy at the bottom where the hook sits */
        .overlay {{
            position: absolute; inset: 0;
            background: linear-gradient(180deg,
                rgba(20,18,16,0.45) 0%,
                rgba(20,18,16,0.30) 38%,
                rgba(20,18,16,0.88) 100%);
        }}
        .logo {{
            position: absolute; top: 56px; left: 60px;
            font-family: 'Inter', sans-serif; font-size: 22px; font-weight: 600;
            letter-spacing: 4px; color: #D4A843; text-transform: uppercase;
            text-shadow: 0 2px 8px rgba(0,0,0,0.6);
        }}
        .content {{
            position: absolute; left: 60px; right: 60px; bottom: 90px;
        }}
        .bar {{ width: 88px; height: 7px; background: #D4A843; border-radius: 4px; margin-bottom: 30px; }}
        .hook {{
            font-family: 'Playfair Display', serif; font-weight: 800;
            font-size: 76px; line-height: 1.08; color: #FAF7F2;
            letter-spacing: -0.015em; text-shadow: 0 3px 20px rgba(0,0,0,0.7);
        }}
        .footer {{
            margin-top: 34px; font-family: 'Inter', sans-serif; font-size: 24px;
            font-weight: 600; color: #D4A843; letter-spacing: 0.3px;
            text-shadow: 0 2px 8px rgba(0,0,0,0.6);
        }}
    </style>
</head>
<body>
    <div class="stage">
        <div class="overlay"></div>
        <div class="logo">Crosswalk Wisdom</div>
        <div class="content">
            <div class="bar"></div>
            <div class="hook">{hook}</div>
            <div class="footer">crosswalkwisdom.com</div>
        </div>
    </div>
</body>
</html>"""

        with open(html_file, "w") as f:
            f.write(html_content)

        return html_file

    def render_to_png(self, html_file: str) -> str:
        """Use shot-scraper to render HTML to PNG."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        png_file = f"{self.output_dir}/infographic_{timestamp}.png"

        try:
            # Resolve shot-scraper's full path — cron's minimal PATH can't find
            # it by bare name (it lives in the Python framework bin, not /usr/bin).
            import shutil
            shot = shutil.which("shot-scraper") or \
                "/Library/Frameworks/Python.framework/Versions/3.14/bin/shot-scraper"
            cmd = [
                shot,
                html_file,
                "--output", png_file,
                "--width", str(self.width),
                "--height", str(self.height)
            ]

            print(f"Rendering infographic to PNG: {png_file}")
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0 and os.path.exists(png_file):
                print(f"✓ Infographic saved: {png_file}")
                return png_file
            else:
                print(f"✗ Error rendering PNG: {result.stderr}")
                return None
        except Exception as e:
            print(f"✗ Error running shot-scraper: {e}")
            return None

    def generate_infographic(self, hook: str, pain_point: str) -> str:
        """Generate full infographic (HTML + PNG) over a cinematic photo."""
        print("\nGenerating infographic...")

        # Keep the overlay hook punchy: first sentence, capped ~90 chars
        overlay_hook = hook.split(". ")[0].strip().rstrip(".")
        if len(overlay_hook) > 90:
            overlay_hook = overlay_hook[:88].rsplit(" ", 1)[0] + "…"

        background = self._pick_background(hook)
        if background:
            print(f"  Background: {os.path.basename(background)}")

        # Generate HTML
        html_file = self.generate_html_template(overlay_hook, background)
        print(f"✓ HTML template created: {html_file}")

        # Render to PNG
        png_file = self.render_to_png(html_file)

        if png_file:
            return png_file
        else:
            print("✗ Failed to render infographic")
            return None
