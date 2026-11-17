#!/usr/bin/env python3
"""Le Cahier — vérifier les voix du récit en les réécoutant.

Chaque clip fabriqué par voix_recit.py est retranscrit par un modèle de reconnaissance de la
parole (Whisper : Groq si GROQ_API_KEY existe, sinon OpenAI). On contrôle deux choses :
  · la langue détectée est bien le français (la voix n'a pas basculé sur autre chose) ;
  · les mots entendus ressemblent aux mots attendus.
Les noms inventés (Plume-sur-Encre, Montluisant) s'entendent mal par nature : un écart sur
eux n'est pas une faute de voix. Le script liste les écarts, il ne juge pas à ta place.

Il n'envoie que l'audio de phrases d'histoire déjà publiques dans l'artefact. Aucune clé n'est
affichée.

Usage : python3 le-cahier/engine/verifier_voix.py [--seuil 0.85]
"""

import argparse
import difflib
import os
import re
import sys
import time
import unicodedata
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
import voix_recit as vr  # noqa: E402
import semaine as sm  # noqa: E402

WORKERS = 2  # l'API de reconnaissance limite le débit : mieux vaut lent que des « sans transcription »


def words(s: str) -> list[str]:
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if not 0x300 <= ord(c) <= 0x36F)
    return re.sub(r"[^a-z0-9 ]", " ", s.lower()).split()


def endpoint() -> tuple[str, str, str]:
    if os.environ.get("GROQ_API_KEY"):
        return (
            "https://api.groq.com/openai/v1/audio/transcriptions",
            os.environ["GROQ_API_KEY"],
            "whisper-large-v3",
        )
    if os.environ.get("OPENAI_API_KEY"):
        return (
            "https://api.openai.com/v1/audio/transcriptions",
            os.environ["OPENAI_API_KEY"],
            "whisper-1",
        )
    raise RuntimeError("ni GROQ_API_KEY ni OPENAI_API_KEY dans .env")


def listen(text: str) -> dict[str, Any]:
    url, key, model = endpoint()
    path = vr.clip_path(text)
    for attempt in range(5):
        try:
            with open(path, "rb") as f:
                r = requests.post(
                    url,
                    headers={"Authorization": f"Bearer {key}"},
                    files={"file": (path.name, f, "audio/wav")},
                    data={"model": model, "response_format": "verbose_json", "temperature": "0"},
                    timeout=120,
                )
            if r.ok:
                return r.json()
        except requests.RequestException:
            pass
        time.sleep(3 * (attempt + 1))
    return {}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seuil", type=float, default=0.85, help="ressemblance minimale des mots (0-1)")
    a = ap.parse_args()

    texts = [t for pg in vr.texts_by_page() for t in pg["texts"]]
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        heard = list(ex.map(listen, texts))

    bad_lang, low, silent = [], [], []
    for t, j in zip(texts, heard):
        if not j:
            silent.append(t)
            continue
        if str(j.get("language", "")).lower() not in ("french", "fr"):
            bad_lang.append((t, j.get("language")))
        ratio = difflib.SequenceMatcher(None, words(t), words(j.get("text", ""))).ratio()
        if ratio < a.seuil:
            low.append((ratio, t, j.get("text", "").strip()))

    print(f"{len(texts)} clips réécoutés")
    print(f"  langue autre que le français : {len(bad_lang)}")
    for t, lg in bad_lang:
        print(f"    [{lg}] {t}")
    print(f"  sans transcription : {len(silent)}")
    for t in silent:
        print(f"    {t}")
    print(f"  mots différents (< {a.seuil:.0%}) : {len(low)}")
    for ratio, t, got in sorted(low):
        print(f"    {ratio:.0%}\n      attendu : {t}\n      entendu : {got}")
    return 1 if (bad_lang or silent) else 0


if __name__ == "__main__":
    sys.exit(main())
