#!/usr/bin/env python3
"""Le Cahier — la voix du récit.

Chaque réplique de l'histoire, chaque réponse juste du héros et chaque phrase de carte est dite
par la vraie voix française du cahier (VoiSpark, cartesia « Calm French Woman », choisie à
l'oreille) : une prononciation juste sur n'importe quel appareil, au lieu de la synthèse du
navigateur, qui lit parfois du français avec une voix anglaise.

Une page de l'histoire = une piste (voix-rNN.mp3, 44,1 kHz mono 64 kb/s), chargée seulement
quand la page s'ouvre. Une seule carte de correspondance, voix-recit.js, qui s'ajoute à
VOIX_REC : clé = dStrip(phrase), valeur = [début, durée, "voix-rNN.mp3"]. voix-map.js, réécrit
chaque lundi par semaine.py, n'est jamais touché.

Les clips se gardent dans engine/recit-voix/clips/ : relancer ne paie que les textes neufs ou
modifiés. Ce script ne touche jamais l'artefact ; --install copie les fichiers dans le dossier
du cahier, la publication est une autre étape.

Usage :
  python3 le-cahier/engine/voix_recit.py --limit 3      # essai : 3 clips, rien d'assemblé
  python3 le-cahier/engine/voix_recit.py                # tout fabriquer et assembler
  python3 le-cahier/engine/voix_recit.py --install      # …puis copier dans le-cahier/
  CAHIER_DIR=/chemin python3 …                          # lire / installer ailleurs
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import semaine as sm  # noqa: E402  (tts, build_shard, duration, d_strip, log)

CAHIER = Path(os.environ.get("CAHIER_DIR") or sm.CAHIER)
WORK = sm.ENGINE / "recit-voix"
CLIPS = WORK / "clips"
OUT = WORK / "out"
WORKERS = 3
CPS_MIN, CPS_MAX = 6.0, 30.0  # signes par seconde plausibles pour de la parole française
MIN_DB = -50.0  # en dessous, la piste est quasi muette


def texts_by_page() -> list[dict[str, Any]]:
    env = {**os.environ, "CAHIER_DIR": str(CAHIER)}
    out = subprocess.run(
        ["node", str(Path(__file__).resolve().parent / "recit_textes.cjs")],
        check=True,
        capture_output=True,
        text=True,
        env=env,
    ).stdout
    return json.loads(out)["pages"]


def clip_path(text: str) -> Path:
    key = sm.d_strip(text)[:40]
    h = hashlib.sha1(text.encode("utf-8")).hexdigest()[:8]
    return CLIPS / f"{key}-{h}.wav"


def mean_db(path: Path) -> float:
    """Volume moyen en dB (ffmpeg volumedetect) ; -91 si on n'arrive pas à le lire."""
    r = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af", "volumedetect", "-f", "null", "-"],
        capture_output=True,
        text=True,
    )
    m = re.search(r"mean_volume:\s*(-?[\d.]+)\s*dB", r.stderr)
    return float(m.group(1)) if m else -91.0


def check_clip(text: str, path: Path) -> str | None:
    """Rend None si le clip est plausible, sinon la raison."""
    dur = sm.duration(path)
    cps = len(text) / dur if dur else 0.0
    if not CPS_MIN <= cps <= CPS_MAX:
        return f"{cps:.1f} signes/s ({dur:.1f} s pour {len(text)} signes)"
    db = mean_db(path)
    if db < MIN_DB:
        return f"quasi muet ({db:.0f} dB)"
    return None


def make_clip(text: str) -> tuple[str, str | None]:
    path = clip_path(text)
    if path.exists() and check_clip(text, path) is None:
        return text, None
    for attempt in (1, 2):
        path.unlink(missing_ok=True)
        if not sm.tts(text, path):
            continue
        why = check_clip(text, path)
        if why is None:
            return text, None
        sm.log(f"  voix récit : « {text[:50]} » suspect, essai {attempt} — {why}")
    path.unlink(missing_ok=True)
    return text, "échec ou clip suspect"


def write_map(entries: dict[str, list[Any]]) -> Path:
    head = (
        "/* Le Cahier — la voix du récit : chaque réplique, chaque réponse du héros et chaque phrase de\n"
        "   carte, dite par la vraie voix française (VoiSpark, cartesia « Calm French Woman »).\n"
        '   clé = dStrip(phrase) ; valeur = [début (s), durée (s), "voix-rNN.mp3"], une piste par page.\n'
        "   Fabriqué par le-cahier/engine/voix_recit.py : ne pas éditer à la main. */\n"
    )
    body = (
        "{\n"
        + ",\n".join(json.dumps(k, ensure_ascii=False) + ":" + json.dumps(v) for k, v in entries.items())
        + "\n}"
    )
    tail = (
        "\nif(typeof VOIX_REC !== \"undefined\") Object.assign(VOIX_REC, VOIX_REC_RECIT);\n"
    )
    p = OUT / "voix-recit.js"
    p.write_text(head + "const VOIX_REC_RECIT = " + body + ";" + tail, encoding="utf-8")
    return p


def run(limit: int | None, install: bool) -> int:
    CLIPS.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    pages = texts_by_page()
    uniq: dict[str, str] = {}
    for pg in pages:
        for t in pg["texts"]:
            uniq.setdefault(sm.d_strip(t), t)
    todo = [t for t in uniq.values() if not (clip_path(t).exists())]
    total = sum(len(pg["texts"]) for pg in pages)
    sm.log(f"voix récit : {len(pages)} pages, {total} textes ({len(uniq)} distincts), {len(todo)} à fabriquer")

    batch = todo[:limit] if limit else todo
    failed: list[tuple[str, str]] = []
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        for n, (text, why) in enumerate(ex.map(make_clip, batch), 1):
            if why:
                failed.append((text, why))
            if n % 10 == 0 or n == len(batch):
                sm.log(f"  {n}/{len(batch)} clips")
    if failed:
        for t, why in failed:
            sm.log(f"  ÉCHEC « {t[:60]} » : {why}")
        sm.log(f"voix récit : {len(failed)} clip(s) en échec — rien d'assemblé")
        return 1
    if limit:
        sm.log(f"voix récit : essai de {len(batch)} clips fait — rien d'assemblé")
        return 0

    entries: dict[str, list[Any]] = {}
    shards: list[Path] = []
    for pg in pages:
        name = f"voix-r{pg['id'][1:]}.mp3"
        clips = [clip_path(t) for t in pg["texts"]]
        got = sm.build_shard(clips, OUT / name, name)
        shards.append(OUT / name)
        for t, e in zip(pg["texts"], got):
            entries.setdefault(sm.d_strip(t), e)
    js = write_map(entries)
    size = sum(s.stat().st_size for s in shards)
    sm.log(f"voix récit : {len(shards)} pistes ({size // 1024} Ko), {len(entries)} phrases — {OUT}")
    if install:
        for f in [*shards, js]:
            shutil.copy2(f, CAHIER / f.name)
        sm.log(f"voix récit : installé dans {CAHIER}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--limit", type=int, help="n'en fabriquer que N (essai) et ne rien assembler")
    ap.add_argument("--install", action="store_true", help="copier pistes et carte dans le dossier du cahier")
    a = ap.parse_args()
    return run(a.limit, a.install)


if __name__ == "__main__":
    sys.exit(main())
