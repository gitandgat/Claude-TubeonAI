#!/usr/bin/env python3
"""Le Cahier — la voix des mots seuls (socle, « le ou la », paires minimales).

Même voix que le reste (VoiSpark cartesia « Calm French Woman »), pistes voix-mNN.mp3 de ~120 mots,
carte voix-mots.js fusionnée dans VOIX_REC. Clips en cache dans engine/recit-voix/clips/.
Usage : CAHIER_DIR=<dossier> python3 engine/voix_mots.py [--install]
"""
import argparse, json, os, shutil, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import semaine as sm  # noqa: E402
import voix_recit as vr  # noqa: E402

CHUNK = 120


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--install", action="store_true")
    a = ap.parse_args()
    texts = json.loads(subprocess.run(
        ["node", str(Path(__file__).resolve().parent / "mots_textes.cjs")], check=True, capture_output=True,
        text=True, env={**os.environ, "CAHIER_DIR": str(vr.CAHIER)}).stdout)["texts"]
    seen, uniq = set(), []
    for t in texts:
        k = sm.d_strip(t)
        if k and k not in seen:
            seen.add(k); uniq.append(t)
    vr.CLIPS.mkdir(parents=True, exist_ok=True); vr.OUT.mkdir(parents=True, exist_ok=True)
    todo = [t for t in uniq if not vr.clip_path(t).exists()]
    sm.log(f"voix mots : {len(uniq)} mots, {len(todo)} à fabriquer")

    def mk(t):
        p = vr.clip_path(t)
        for _ in range(3):
            if sm.tts(t, p) and sm.duration(p) > 0.2 and vr.mean_db(p) > vr.MIN_DB:
                return t, None
        p.unlink(missing_ok=True)
        return t, "échec"
    with ThreadPoolExecutor(max_workers=vr.WORKERS) as ex:
        bad = [r for r in ex.map(mk, todo) if r[1]]
    if bad:
        sm.log(f"voix mots : {len(bad)} échecs : {[t for t, _ in bad][:10]}")
        return 1
    entries, files = {}, []
    for n in range(0, len(uniq), CHUNK):
        part = uniq[n:n + CHUNK]
        name = f"voix-m{n // CHUNK:02d}.mp3"
        got = sm.build_shard([vr.clip_path(t) for t in part], vr.OUT / name, name)
        files.append(vr.OUT / name)
        for t, e in zip(part, got):
            entries[sm.d_strip(t)] = e
    body = "{\n" + ",\n".join(json.dumps(k, ensure_ascii=False) + ":" + json.dumps(v) for k, v in entries.items()) + "\n}"
    js = vr.OUT / "voix-mots.js"
    js.write_text("/* Le Cahier — les mots seuls, dits par la vraie voix. Fabriqué par engine/voix_mots.py : ne pas éditer. */\n"
                  "const VOIX_REC_MOTS = " + body + ";\n"
                  'if(typeof VOIX_REC !== "undefined") Object.assign(VOIX_REC, VOIX_REC_MOTS);\n', encoding="utf-8")
    sm.log(f"voix mots : {len(files)} pistes, {sum(f.stat().st_size for f in files)//1024} Ko, {len(entries)} mots")
    if a.install:
        for f in [*files, js]:
            shutil.copy2(f, vr.CAHIER / f.name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
