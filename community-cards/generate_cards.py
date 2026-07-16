"""
Generate brand cards for community launch posts.
5 Facebook posts + 1 LinkedIn teaser.
"""
import subprocess
import os

os.makedirs("/Users/toto/Claude TubeonAI/community-cards/output", exist_ok=True)

CARDS = [
    {
        "id": "linkedin-teaser",
        "tag": "CROSSWALK WISDOM",
        "hook_1": "I went quiet",
        "hook_2": "for a while.",
        "sub": "Here's what I've been figuring out about why IMGs stay stuck.",
        "out": "linkedin-teaser.png",
    },
    {
        "id": "fb-01-welcome",
        "tag": "THE CROSSWALK COMMUNITY",
        "hook_1": "Done pretending",
        "hook_2": "you're fine?",
        "sub": "This is the space for IMGs in Canada who are ready to ask the real question.",
        "out": "fb-01-welcome.png",
    },
    {
        "id": "fb-02-sunk-cost",
        "tag": "CROSSWALK WISDOM",
        "hook_1": "\"You've come",
        "hook_2": "too far to quit.\"",
        "sub": "That's not wisdom. That's a trap with a respectable name.",
        "out": "fb-02-sunk-cost.png",
    },
    {
        "id": "fb-03-identity",
        "tag": "CROSSWALK WISDOM",
        "hook_1": "This isn't",
        "hook_2": "a career problem.",
        "sub": "It's an identity problem. And you can't job-board your way out of that.",
        "out": "fb-03-identity.png",
    },
    {
        "id": "fb-04-fear",
        "tag": "CROSSWALK WISDOM",
        "hook_1": "What are you",
        "hook_2": "actually afraid of?",
        "sub": "Not your concerns — your fears. Name them. They're almost never about the job.",
        "out": "fb-04-fear.png",
    },
    {
        "id": "fb-05-cta",
        "tag": "CROSSWALK WISDOM",
        "hook_1": "5 minutes.",
        "hook_2": "Real clarity.",
        "sub": "The Fear Audit helps you separate what's real from the noise. Free. No pitch.",
        "out": "fb-05-cta.png",
    },
]

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Inter:wght@400;600&display=swap');
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    width: 1080px; height: 1080px;
    background: #1e1e1e;
    font-family: 'Playfair Display', serif;
    display: flex; align-items: center; justify-content: center;
    overflow: hidden;
  }}
  .card {{
    width: 1080px; height: 1080px;
    padding: 72px 80px;
    display: flex; flex-direction: column; justify-content: space-between;
    position: relative;
  }}
  /* stripe motif */
  .card::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 8px;
    background: linear-gradient(90deg, #d4a574 0%, #2ec4b6 100%);
  }}
  /* subtle corner texture */
  .card::after {{
    content: '';
    position: absolute;
    bottom: -120px; right: -120px;
    width: 400px; height: 400px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(212,165,116,0.07) 0%, transparent 70%);
  }}
  .tag {{
    font-family: 'Inter', sans-serif;
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #2ec4b6;
  }}
  .hook {{
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    padding: 40px 0;
  }}
  .hook-line-1 {{
    font-size: 82px;
    font-weight: 400;
    line-height: 1.05;
    color: #f0ede8;
  }}
  .hook-line-2 {{
    font-size: 82px;
    font-weight: 700;
    line-height: 1.05;
    color: #d4a574;
  }}
  .sub {{
    font-family: 'Inter', sans-serif;
    font-size: 22px;
    font-weight: 400;
    color: #a0a0a0;
    line-height: 1.5;
    max-width: 760px;
  }}
  .footer {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-top: 32px;
  }}
  .brand {{
    font-family: 'Inter', sans-serif;
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 2px;
    color: #555;
    text-transform: uppercase;
  }}
  .accent-dot {{
    width: 10px; height: 10px;
    border-radius: 50%;
    background: #d4a574;
    display: inline-block;
    margin-left: 8px;
  }}
</style>
</head>
<body>
<div class="card">
  <div class="tag">{tag}</div>
  <div class="hook">
    <div class="hook-line-1">{hook_1}</div>
    <div class="hook-line-2">{hook_2}</div>
  </div>
  <div>
    <div class="sub">{sub}</div>
    <div class="footer">
      <div class="brand">crosswalkwisdom.com</div>
      <span class="accent-dot"></span>
    </div>
  </div>
</div>
</body>
</html>"""

BASE = "/Users/toto/Claude TubeonAI/community-cards"

for card in CARDS:
    html_path = f"{BASE}/{card['id']}.html"
    out_path = f"{BASE}/output/{card['out']}"

    html = HTML_TEMPLATE.format(
        tag=card["tag"],
        hook_1=card["hook_1"],
        hook_2=card["hook_2"],
        sub=card["sub"],
    )
    with open(html_path, "w") as f:
        f.write(html)

    result = subprocess.run(
        ["shot-scraper", html_path, "-o", out_path, "--width", "1080", "--height", "1080"],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        print(f"✓ {card['out']}")
    else:
        print(f"✗ {card['out']}: {result.stderr.strip()}")
