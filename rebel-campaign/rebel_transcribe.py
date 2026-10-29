#!/usr/bin/env python3
"""
Replacement transcriber using faster-whisper (avoids whisperx/numba numpy conflict).
Produces the same words.json format as the video-edit skill's transcribe.py:
  [{"word": str, "start": float, "end": float}, ...]

Usage:
  python rebel_transcribe.py <video_path> [model_size]
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

CACHE = Path.home() / ".cache" / "video-edit"
BREW_BIN = "/opt/homebrew/bin"


def workdir_for(video_path: Path) -> Path:
    p = video_path.resolve()
    digest = hashlib.sha1(str(p).encode()).hexdigest()[:12]
    return CACHE / f"{p.stem[:40]}_{digest}"


def extract_audio(video_path: Path, audio_path: Path) -> None:
    env = {**os.environ, "PATH": BREW_BIN + ":" + os.environ.get("PATH", "")}
    subprocess.run(
        [
            "ffmpeg", "-y", "-i", str(video_path),
            "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le",
            str(audio_path),
        ],
        env=env,
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def transcribe(audio_path: Path, model_size: str = "base") -> list[dict]:
    from faster_whisper import WhisperModel  # type: ignore

    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    segments, _ = model.transcribe(str(audio_path), word_timestamps=True)

    words: list[dict] = []
    for seg in segments:
        for w in (seg.words or []):
            if w.word and w.start is not None and w.end is not None:
                words.append({
                    "word": w.word.strip(),
                    "start": round(float(w.start), 3),
                    "end": round(float(w.end), 3),
                })
    return words


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: rebel_transcribe.py <video_path> [model_size]", file=sys.stderr)
        return 2

    video_path = Path(sys.argv[1]).expanduser().resolve()
    if not video_path.exists():
        print(f"video not found: {video_path}", file=sys.stderr)
        return 1

    model_size = sys.argv[2] if len(sys.argv) > 2 else os.environ.get("WHISPER_MODEL", "base")

    wd = workdir_for(video_path)
    wd.mkdir(parents=True, exist_ok=True)
    words_json = wd / "words.json"

    if (words_json.exists()
            and words_json.stat().st_mtime >= video_path.stat().st_mtime
            and os.environ.get("FORCE") != "1"):
        print(f"words.json fresh, skipping: {words_json}")
        return 0

    audio_path = wd / "audio.wav"
    print(f"[1/2] Extracting audio -> {audio_path}", flush=True)
    extract_audio(video_path, audio_path)

    print(f"[2/2] Transcribing with faster-whisper (model={model_size})", flush=True)
    words = transcribe(audio_path, model_size)
    words_json.write_text(json.dumps(words, indent=2))
    print(f"Wrote {len(words)} words -> {words_json}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
