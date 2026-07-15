#!/usr/bin/env python3
"""
Generate voiceovers for all 27 content pieces using VoiSpark API
"""

import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

VOISPARK_API_KEY = os.getenv('VOISPARK_API_KEY')
if not VOISPARK_API_KEY:
    raise ValueError("VOISPARK_API_KEY not set")

DRAFTS_DIR = "drafts/blog-social"
OUTPUT_DIR = "tiktok-voiceovers"

def get_text_for_voiceover(text):
    """Extract and shorten text for voiceover (max ~90 words for TikTok)"""
    # Take first few sentences/paragraphs
    lines = text.strip().split('\n')
    voiceover_text = ""
    word_count = 0

    for line in lines:
        if not line.strip():
            continue
        words = len(line.split())
        if word_count + words > 90:
            break
        voiceover_text += line + " "
        word_count += words

    return voiceover_text.strip()

def generate_voiceover(text, slug):
    """Generate voiceover using VoiSpark API"""

    voiceover_text = get_text_for_voiceover(text)

    print(f"  {slug}: {len(voiceover_text.split())} words")

    try:
        response = requests.post(
            "https://api.voispark.com/api/tts/generate",
            headers={"Authorization": f"Bearer {VOISPARK_API_KEY}"},
            json={
                "text": voiceover_text,
                "provider": "openai",
                "model": "tts-1",
                "voice": "onyx",
                "sync": True
            },
            timeout=30
        )

        if response.status_code != 200:
            print(f"    Error: {response.status_code} - {response.text[:100]}")
            return None

        data = response.json()
        audio_url = data.get('data', {}).get('details', {}).get('url')

        if not audio_url:
            print(f"    Error: No audio URL in response")
            return None

        # Download audio
        audio_response = requests.get(audio_url, timeout=30)
        if audio_response.status_code != 200:
            print(f"    Error downloading audio: {audio_response.status_code}")
            return None

        # Save locally
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        audio_path = f"{OUTPUT_DIR}/{slug}-voiceover.wav"
        with open(audio_path, 'wb') as f:
            f.write(audio_response.content)

        print(f"    ✓ Saved: {audio_path}")
        return audio_path

    except Exception as e:
        print(f"    Error: {str(e)}")
        return None

def main():
    print("=" * 70)
    print("Generate TikTok Voiceovers from Content")
    print("=" * 70 + "\n")

    drafts_path = Path(DRAFTS_DIR)
    voiceovers = {}

    for content_dir in sorted(drafts_path.iterdir()):
        if not content_dir.is_dir():
            continue

        slug = content_dir.name
        linkedin_file = content_dir / "linkedin.md"

        if not linkedin_file.exists():
            print(f"✗ {slug}: No linkedin.md found")
            continue

        with open(linkedin_file, 'r') as f:
            content = f.read()

        audio_path = generate_voiceover(content, slug)
        if audio_path:
            voiceovers[slug] = audio_path

    # Summary
    print("\n" + "=" * 70)
    print(f"Generated {len(voiceovers)}/{len(list(drafts_path.iterdir()))} voiceovers")
    print("=" * 70)

    # Save mapping
    with open('tiktok-voiceovers-map.json', 'w') as f:
        json.dump(voiceovers, f, indent=2)

    print("\nVoiceover mapping saved to tiktok-voiceovers-map.json")

if __name__ == '__main__':
    main()
