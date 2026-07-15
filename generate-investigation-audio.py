#!/usr/bin/env python3
"""Generate onyx VoiSpark narration + faster-whisper word alignment for the
investigation-video series, writing audio_meta.json per project.

Bypasses the HyperFrames faceless-explainer skill's built-in `audio.mjs generate`
engine (../hyperframes-media/scripts/audio.mjs), which does not exist in this repo.
Per-frame WAVs go to videos/<slug>/assets/voice/NN.wav; word timings are frame-
relative (0-based per clip) per captions.mjs's consumption contract.

Voice: onyx (OpenAI gpt-4o-mini-tts) via VoiSpark. Schema confirmed in
generate-moveassess-voiceovers.py. Do NOT add a `configs` key (err 40214).

Run (uses the repo's .venv-audio for faster-whisper):
    .venv-audio/bin/python3 generate-investigation-audio.py                # all 4
    .venv-audio/bin/python3 generate-investigation-audio.py investigation-glutes
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

HERE = Path(__file__).resolve().parent
load_dotenv(HERE / ".env")

VOISPARK_URL = "https://api.voispark.com/api/tts/generate"
VIDEOS_DIR = HERE / "videos"
WHISPER_MODEL_SIZE = os.environ.get("WHISPER_MODEL", "base")

ALL_SLUGS = [
    "investigation-glutes",
    "investigation-stuck",
    "investigation-walking",
    "investigation-indecision",
]

LINE_RE = re.compile(
    r"^## Line \d+.*\(Frame (\d+)\)\s*$", re.MULTILINE
)


def parse_script(script_path: Path) -> list[dict]:
    """Return [{frame, text}] parsed from a faceless-explainer SCRIPT.md."""
    text = script_path.read_text()
    matches = list(LINE_RE.finditer(text))
    lines = []
    for i, m in enumerate(matches):
        frame = int(m.group(1))
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        block = text[start:end]
        # Spoken text is the block's last non-empty paragraph, after the
        # **Time:** / **Delivery:** metadata lines.
        body_lines = [
            ln.strip() for ln in block.splitlines()
            if ln.strip() and not ln.strip().startswith("**")
        ]
        if not body_lines:
            raise SystemExit(f"No spoken text found for Frame {frame} in {script_path}")
        spoken = " ".join(body_lines)
        lines.append({"frame": frame, "text": spoken})
    if not lines:
        raise SystemExit(f"No '## Line N (Frame M)' headers found in {script_path}")
    return lines


def voispark_tts(text: str, out_wav: Path) -> Path:
    key = os.environ.get("VOISPARK_API_KEY")
    if not key:
        raise SystemExit("VOISPARK_API_KEY not found in .env")
    resp = requests.post(
        VOISPARK_URL,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        json={
            "text": text,
            "provider": "openai",
            "model_id": "gpt-4o-mini-tts",
            "voice": {"type": "preset", "voice_id": "onyx"},
            "sync": True,
        },
        timeout=180,
    )
    resp.raise_for_status()
    payload = resp.json()
    data = payload.get("data") or {}
    if data.get("status") == "failed":
        raise SystemExit(f"VoiSpark task failed: {data.get('error')}")
    try:
        url = data["details"]["url"]
    except (KeyError, TypeError) as exc:
        raise SystemExit(f"Unexpected VoiSpark response shape: {payload}") from exc
    audio = requests.get(url, timeout=180)
    audio.raise_for_status()
    out_wav.parent.mkdir(parents=True, exist_ok=True)
    out_wav.write_bytes(audio.content)
    return out_wav


def duration_seconds(wav: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(wav)],
        capture_output=True, text=True, check=True,
    )
    return float(out.stdout.strip())


_WHISPER_MODEL = None


def get_whisper_model():
    global _WHISPER_MODEL
    if _WHISPER_MODEL is None:
        from faster_whisper import WhisperModel
        print(f"  (loading faster-whisper model={WHISPER_MODEL_SIZE} ...)", flush=True)
        _WHISPER_MODEL = WhisperModel(WHISPER_MODEL_SIZE, device="cpu", compute_type="int8")
    return _WHISPER_MODEL


def align_words(wav: Path) -> list[dict]:
    """Frame-relative (0-based) word timings: [{text, start, end}, ...]."""
    model = get_whisper_model()
    segments, _ = model.transcribe(str(wav), word_timestamps=True)
    words = []
    for seg in segments:
        for w in (seg.words or []):
            if w.word and w.start is not None and w.end is not None:
                words.append({
                    "text": w.word.strip(),
                    "start": round(float(w.start), 3),
                    "end": round(float(w.end), 3),
                })
    return words


def process_project(slug: str) -> None:
    project_dir = VIDEOS_DIR / slug
    script_path = project_dir / "SCRIPT.md"
    if not script_path.exists():
        print(f"! {slug}: no SCRIPT.md, skipping")
        return

    print(f"\n=== {slug} ===")
    lines = parse_script(script_path)
    voice_dir = project_dir / "assets" / "voice"
    voices = []

    for line in lines:
        frame = line["frame"]
        rel_path = f"assets/voice/{frame:02d}.wav"
        out_wav = project_dir / rel_path
        print(f"  Frame {frame}: TTS ...", end=" ", flush=True)
        voispark_tts(line["text"], out_wav)
        dur = duration_seconds(out_wav)
        print(f"{dur:.2f}s, aligning ...", end=" ", flush=True)
        words = align_words(out_wav)
        print(f"{len(words)} words")
        voices.append({
            "frame": frame,
            "path": rel_path,
            "duration_s": round(dur, 3),
            "words": words,
        })

    audio_meta = {"bgm": None, "voices": voices, "sfx": []}
    meta_path = project_dir / "audio_meta.json"
    meta_path.write_text(json.dumps(audio_meta, indent=2) + "\n")
    print(f"  wrote {meta_path}")


def main() -> int:
    slugs = sys.argv[1:] or ALL_SLUGS
    for slug in slugs:
        if slug not in ALL_SLUGS:
            print(f"! unknown slug {slug}, skipping")
            continue
        process_project(slug)
    print("\nDone.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
