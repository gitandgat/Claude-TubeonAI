#!/usr/bin/env python3
"""Le Cahier — le moteur de la semaine.

Chaque lundi : vingt phrases à trous neuves, au niveau et sur les sujets de
l'apprenant, chacune dite par la vraie voix française du cahier (VoiSpark,
cartesia « Calm French Woman », choisie à l'oreille). Sortie dans
le-cahier/engine/out/<semaine>/ :

  phrases.js       TROU_PLUS complet (anciennes + nouvelles)
  voix-map.js      VOIX_REC complet (anciennes + nouvelles, avec leur piste)
  voix-AAwSS.mp3   la piste de la semaine (44,1 kHz mono 64 kb/s, comme voix.mp3)
  manifest.json    ce qui a été fait, et sur quelle base

Ce script ne touche jamais l'artefact. La publication est l'étape d'après
(skill le-cahier-publier), qui rappelle ce script avec --mark-published pour
recopier les fichiers dans le miroir le-cahier/.

Usage :
  python3 le-cahier/engine/semaine.py                  # semaine en cours, 20 phrases
  python3 le-cahier/engine/semaine.py --dry-run --n 2  # essai, dans out/dry-<semaine>/
  python3 le-cahier/engine/semaine.py --pending        # code 0 s'il reste une semaine à publier
  python3 le-cahier/engine/semaine.py --pending --print
  python3 le-cahier/engine/semaine.py --mark-published 2026-W46 --version 46
  python3 le-cahier/engine/semaine.py --profile-from progress.json
  python3 le-cahier/engine/semaine.py --selftest       # dStrip identique au JavaScript ?
"""

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import unicodedata
import logging
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
CAHIER = ROOT / "le-cahier"
ENGINE = CAHIER / "engine"
OUT = ENGINE / "out"
STATE = ENGINE / "state.json"
PROFILE = ENGINE / "profil.json"
LOG = ROOT / "logs" / "le_cahier_semaine.log"
load_dotenv(ROOT / ".env")

VOISPARK = "https://api.voispark.com/api"
VOICE_ID = "a8a1eb38-5f15-4c1d-8722-7ac0f329727d"  # Calm French Woman
VOICE_MODEL = "sonic-3.6"
MODELS = [m for m in os.environ.get("LE_CAHIER_MODELS", "").split(",") if m] or [
    "claude-opus-5-5",
    "claude-fable-5-1",
    "claude-opus-5",
    "claude-sonnet-5",
]

PRE, POST = 0.10, 0.35  # silence avant / après chaque phrase (s)
LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"]
DOMAINS = {
    "sante": "Santé et soins",
    "travail": "Travail et réunions",
    "quotidien": "Vie quotidienne",
    "admin": "Démarches et administration",
    "actu": "Actualité et débat",
    "voyage": "Voyage et transports",
    "famille": "Famille et amis",
    "cuisine": "Cuisine et marché",
    "sport": "Sport et santé physique",
    "culture": "Films, livres, musique",
}


# ---------------------------------------------------------------- utilitaires


def _logger() -> logging.Logger:
    lg = logging.getLogger("le-cahier-semaine")
    if not lg.handlers:
        LOG.parent.mkdir(parents=True, exist_ok=True)
        fmt = logging.Formatter("%(asctime)s  %(message)s", "%Y-%m-%d %H:%M")
        for h in (
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(LOG, encoding="utf-8"),
        ):
            h.setFormatter(fmt)
            lg.addHandler(h)
        lg.setLevel(logging.INFO)
        lg.propagate = False
    return lg


def log(msg: str) -> None:
    _logger().info(msg)


def d_strip(s: str) -> str:
    """Même clé que dStrip() de dictee.js : sans accents, minuscules, a-z0-9."""
    s = unicodedata.normalize("NFD", str(s))
    s = "".join(ch for ch in s if not (0x300 <= ord(ch) <= 0x36F))
    return re.sub(r"[^a-z0-9]", "", s.lower())


def sha256(path: Path | str) -> str | None:
    return (
        hashlib.sha256(Path(path).read_bytes()).hexdigest()
        if Path(path).exists()
        else None
    )


def week_of(day: dt.date | None = None) -> tuple[str, str]:
    y, w, _ = (day or dt.date.today()).isocalendar()
    return f"{y}-W{w:02d}", f"{y % 100:02d}w{w:02d}"


def load_state() -> dict[str, Any]:
    try:
        return json.loads(STATE.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {"weeks": {}}


def save_state(st: dict[str, Any]) -> None:
    STATE.write_text(
        json.dumps(st, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )


def read_js_json(path: Path | str, name: str) -> Any:
    """Le littéral JSON après « const NAME = » dans un fichier du cahier."""
    src = Path(path).read_text(encoding="utf-8")
    m = re.search(r"const " + name + r" = (.*?);\s*$", src, re.S | re.M)
    if not m:
        raise ValueError(f"{name} introuvable dans {path}")
    return json.loads(m.group(1))


def trou_sentences() -> list[str]:
    """Les phrases du socle (TROU dans cahier.js), complétées."""
    src = (CAHIER / "cahier.js").read_text(encoding="utf-8")
    out = []
    for m in re.finditer(
        r'id:"(t\d+)",\s*s:"((?:[^"\\]|\\.)*)",\s*a:"((?:[^"\\]|\\.)*)"', src
    ):
        s, a = json.loads('"' + m.group(2) + '"'), json.loads('"' + m.group(3) + '"')
        out.append(s.replace("___", a))
    return out


def load_profile() -> dict[str, Any]:
    base = {"level": 2, "domains": ["quotidien"], "why": "", "l1": ""}
    try:
        base.update(json.loads(PROFILE.read_text(encoding="utf-8")))
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    base["level"] = max(1, min(6, int(base.get("level") or 2)))
    base["domains"] = [d for d in base.get("domains") or [] if d in DOMAINS] or [
        "quotidien"
    ]
    return base


# ---------------------------------------------------------------- génération


def gen_prompt(n: int, prof: dict[str, Any], avoid_recent: list[str]) -> str:
    lv = prof["level"]
    low = max(1, lv - 1)
    k_low = n // 3 if lv > 1 else 0
    k_hi = n - k_low
    levels = (
        f"{k_hi} phrases au niveau {LEVELS[lv - 1]} et {k_low} au niveau {LEVELS[low - 1]}"
        if k_low
        else f"{n} phrases au niveau {LEVELS[lv - 1]}"
    )
    doms = ", ".join(DOMAINS[d] for d in prof["domains"])
    recent = "\n".join("- " + s for s in avoid_recent[-40:])
    return (
        "Tu fabriques des phrases à trous de français pour un apprenant précis. "
        f"Écris {n} phrases.\n\n"
        f"Niveaux : {levels}. Rien au-dessus de {LEVELS[lv - 1]}.\n"
        + (f"Pourquoi il apprend : {prof['why']}\n" if prof.get("why") else "")
        + f"Ses sujets, à répartir : {doms}.\n"
        + (
            f"Sa langue la plus forte : {prof['l1']}. Vise les erreurs typiques qu'elle lui fait "
            "faire (faux amis, prépositions, genre des noms).\n"
            if prof.get("l1")
            else ""
        )
        + "\nRègles :\n"
        "- Des phrases qu'il pourrait vraiment entendre ou dire dans ces domaines, au Canada ou "
        "ailleurs. Rien qui sente le manuel.\n"
        "- Entre 7 et 16 mots, ponctuation française correcte (espace avant ? ! : ;).\n"
        "- Un seul mot ou une seule expression remplacée par ___ (trois tirets bas). Jamais un "
        "mot grammatical banal comme « le », « de », « et ».\n"
        "- La réponse n'apparaît nulle part ailleurs dans la phrase.\n"
        "- 3 distracteurs de même nature grammaticale, plausibles ailleurs mais faux ici.\n"
        "- Les distracteurs s'accordent avec ce qui entoure le trou : même genre et même nombre "
        "que l'article ou l'adjectif voisin, même construction (« à la ___ » → trois noms "
        "féminins). Seul le sens doit les éliminer, jamais un article ou un accord.\n"
        "- Une traduction anglaise naturelle de la phrase complète, trou rempli.\n"
        "- Aucun guillemet droit (\") dans les textes : si une phrase cite quelqu'un, utilise « ».\n"
        "- Chaque phrase sera lue à voix haute par une voix française : aucun chiffre (écris les "
        "nombres en lettres), aucune abréviation, aucun sigle.\n"
        "- Vérifie chaque phrase en y remettant la réponse : elle doit être grammaticale, "
        "accords compris, et naturelle pour un francophone.\n"
        + (
            f"- N'écris aucune de ces phrases déjà connues, ni de variante proche :\n{recent}\n"
            if recent
            else ""
        )
        + '\nRéponds uniquement par un tableau JSON d\'objets {"s","a","d","g","lv"}, '
        "où lv est le niveau de 1 à 6 :\n"
        '[{"s":"Le patient se plaint d\'une douleur ___ depuis trois jours.","a":"persistante",'
        '"d":["bruyante","gratuite","salée"],"g":"The patient has had a persistent pain for '
        'three days.","lv":2}]'
    )


def extract_json_array(text: str) -> list[Any]:
    a, b = text.find("["), text.rfind("]")
    if a < 0 or b <= a:
        raise ValueError("pas de tableau JSON dans la réponse")
    return json.loads(text[a : b + 1])


def ask_claude(prompt: str) -> tuple[list[Any], str]:
    import anthropic

    client = anthropic.Anthropic()
    last = None
    for model in MODELS:
        try:
            msg = client.messages.create(
                model=model,
                max_tokens=6000,
                messages=[{"role": "user", "content": prompt}],
            )
            text = "".join(getattr(b, "text", "") for b in msg.content)
            try:
                return extract_json_array(text), model
            except ValueError as bad:  # JSONDecodeError is a ValueError
                # One repair round: same answer, strict JSON. A model that wrote good
                # sentences with one stray quote shouldn't cost the whole week.
                log(
                    f"  {model} : JSON invalide ({str(bad)[:80]}) — on demande une correction"
                )
                fix = client.messages.create(
                    model=model,
                    max_tokens=6000,
                    messages=[
                        {"role": "user", "content": prompt},
                        {"role": "assistant", "content": text},
                        {
                            "role": "user",
                            "content": "Ta réponse n'est pas un JSON valide ("
                            + str(bad)[:120]
                            + "). Renvoie exactement le même tableau, corrigé, en JSON "
                            "strict : aucun guillemet droit dans les textes (utilise « »), "
                            "rien avant ni après le tableau.",
                        },
                    ],
                )
                fixed = "".join(getattr(b, "text", "") for b in fix.content)
                return extract_json_array(fixed), model
        except (anthropic.NotFoundError, anthropic.PermissionDeniedError) as e:
            last = e
            log(
                f"  modèle {model} indisponible ({type(e).__name__}) — on essaie le suivant"
            )
        except anthropic.BadRequestError as e:
            if "model" in str(e).lower():
                last = e
                log(f"  modèle {model} refusé — on essaie le suivant")
                continue
            raise
    raise RuntimeError(f"aucun modèle utilisable : {last}")


def word_in(word: str, text: str) -> bool:
    return (
        re.search(r"(?<![\wÀ-ÿœ])" + re.escape(word) + r"(?![\wÀ-ÿœ])", text, re.I)
        is not None
    )


def validate(
    item: Any, prof: dict[str, Any], seen: set[str]
) -> tuple[dict[str, Any] | None, str | None]:
    """Une phrase reçue est-elle utilisable telle quelle ? Rend (entrée, raison)."""
    if not isinstance(item, dict):
        return None, "pas un objet"
    s, a, d, g = item.get("s"), item.get("a"), item.get("d"), item.get("g")
    if not (
        isinstance(s, str)
        and isinstance(a, str)
        and isinstance(g, str)
        and isinstance(d, list)
    ):
        return None, "champ manquant"
    s, a, g = s.strip(), a.strip(), g.strip()
    if s.count("___") != 1 or not a or len(a) > 40 or not g or len(g) > 220:
        return None, "trou ou champ invalide"
    full = s.replace("___", a)
    n_words = len(full.split())
    if not 6 <= n_words <= 18:
        return None, f"{n_words} mots"
    if re.search(r"\d", full):
        return None, "chiffres"
    if word_in(a, s.replace("___", " ")):
        return None, "réponse visible dans la phrase"
    dd = [x.strip() for x in d if isinstance(x, str) and x.strip()]
    if (
        len(dd) != 3
        or len({x.lower() for x in dd}) != 3
        or a.lower() in {x.lower() for x in dd}
    ):
        return None, "distracteurs"
    key = d_strip(full)
    if key in seen:
        return None, "déjà connue"
    lv = item.get("lv")
    lv = lv if isinstance(lv, int) and 1 <= lv <= 6 else prof["level"]
    lv = max(max(1, prof["level"] - 1), min(prof["level"], lv))
    return {"s": s, "a": a, "d": dd, "g": g, "lv": lv}, None


def generate(
    n: int, prof: dict[str, Any], seen: set[str], recent: list[str]
) -> tuple[list[dict[str, Any]], str | None]:
    kept, tries = [], 0
    model_used = None
    while len(kept) < n and tries < 3:
        tries += 1
        want = n - len(kept)
        prompt = gen_prompt(
            want + (2 if tries == 1 else 1),
            prof,
            recent + [k["s"].replace("___", k["a"]) for k in kept],
        )
        try:
            raw, model_used = ask_claude(prompt)
        except ValueError as e:  # still not JSON after the repair round: spend a try, go on
            log(f"  essai {tries} perdu : réponse illisible ({str(e)[:100]})")
            continue
        log(f"  {model_used} : {len(raw)} phrases reçues (essai {tries})")
        for it in raw:
            e, why = validate(it, prof, seen)
            if e:
                kept.append(e)
                seen.add(d_strip(e["s"].replace("___", e["a"])))
                if len(kept) >= n:
                    break
            else:
                log(
                    f"  écartée ({why}) : {str(it.get('s') if isinstance(it, dict) else it)[:70]}"
                )
    return kept, model_used


# ---------------------------------------------------------------- la voix


def tts(text: str, out_wav: Path) -> bool:
    key = os.environ.get("VOISPARK_API_KEY")
    if not key:
        raise RuntimeError("VOISPARK_API_KEY absente de .env")
    h = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    body = {
        "text": text,
        "provider": "cartesia",
        "model_id": VOICE_MODEL,
        "voice": {"type": "preset", "voice_id": VOICE_ID},
        "sync": True,
    }
    for attempt in range(3):
        try:
            r = requests.post(
                f"{VOISPARK}/tts/generate", headers=h, json=body, timeout=120
            )
            j = r.json() if r.ok else {}
            url = ((j.get("data") or {}).get("details") or {}).get("url")
            if j.get("code") == 0 and url:
                a = requests.get(url, timeout=120)
                if a.ok and a.content[:4] == b"RIFF":
                    Path(out_wav).write_bytes(a.content)
                    return True
            log(f"  voix : réponse inattendue ({r.status_code}) — {str(j)[:160]}")
        except (requests.RequestException, ValueError) as e:
            log(f"  voix : {type(e).__name__} {str(e)[:120]}")
        time.sleep(4 * (attempt + 1))
    return False


def ff(*args: str) -> None:
    subprocess.run(
        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *args], check=True
    )


def duration(path: Path | str) -> float:
    out = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=nw=1:nk=1",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    return float(out)


def build_shard(
    clips: list[Path], shard_path: Path, shard_name: str
) -> list[list[Any]]:
    """Assemble les phrases en une piste ; rend [début, durée, piste] pour chacune."""
    tmp = Path(tempfile.mkdtemp(prefix="cahier-"))
    try:
        pre, post = tmp / "pre.wav", tmp / "post.wav"
        for p, sec in ((pre, PRE), (post, POST)):
            ff(
                "-f",
                "lavfi",
                "-i",
                "anullsrc=r=44100:cl=mono",
                "-t",
                f"{sec:.3f}",
                "-c:a",
                "pcm_s16le",
                str(p),
            )
        listing, entries, t = [], [], 0.0
        for i, c in enumerate(clips):
            norm = tmp / f"c{i:02d}.wav"
            ff("-i", str(c), "-ar", "44100", "-ac", "1", "-c:a", "pcm_s16le", str(norm))
            dur = duration(norm)
            entries.append([round(t, 2), round(PRE + dur, 2), shard_name])
            t += PRE + dur + POST
            listing += [f"file '{pre}'", f"file '{norm}'", f"file '{post}'"]
        (tmp / "list.txt").write_text("\n".join(listing) + "\n", encoding="utf-8")
        ff(
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(tmp / "list.txt"),
            "-c:a",
            "libmp3lame",
            "-b:a",
            "64k",
            "-ar",
            "44100",
            "-ac",
            "1",
            str(shard_path),
        )
        got = duration(shard_path)
        if abs(got - t) > 0.25:
            raise RuntimeError(f"piste de {got:.2f} s au lieu de {t:.2f} s")
        return entries
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------------- sorties


def write_phrases(path: Path | str, items: list[dict[str, Any]]) -> None:
    head = (
        "/* Le Cahier — les phrases de la semaine (phrases à trous, voix enregistrée).\n"
        "   Chaque entrée : {id, s, a, d, g, lv, w}. Ajoutées chaque lundi par\n"
        "   le-cahier/engine/semaine.py : ne pas éditer à la main. */\n"
    )
    body = (
        "[\n" + ",\n".join(json.dumps(e, ensure_ascii=False) for e in items) + "\n]"
        if items
        else "[]"
    )
    Path(path).write_text(head + "const TROU_PLUS = " + body + ";\n", encoding="utf-8")


def write_voix(path: Path | str, rec: dict[str, list[Any]]) -> None:
    head = (
        "/* Le Cahier — la carte des phrases enregistrées.\n"
        "   clé = dStrip(phrase) ; valeur = [début (s), durée (s)] dans voix.mp3,\n"
        '   ou [début, durée, "voix-AAwSS.mp3"] pour une piste de la semaine.\n'
        "   Réécrit chaque semaine par le-cahier/engine/semaine.py : ne pas éditer à la main. */\n"
    )
    body = (
        "{\n"
        + ",\n".join(
            json.dumps(k, ensure_ascii=False) + ":" + json.dumps(v)
            for k, v in rec.items()
        )
        + "\n}"
    )
    Path(path).write_text(head + "const VOIX_REC = " + body + ";\n", encoding="utf-8")


# ---------------------------------------------------------------- commandes


def run(n: int, dry: bool, force: bool) -> int:
    week, code = week_of()
    st = load_state()
    w = st["weeks"].get(week, {})
    out = OUT / (("dry-" if dry else "") + week)
    if not dry and w.get("published") and not force:
        log(f"{week} : déjà publiée ({w.get('version', '?')}) — rien à faire")
        return 0
    if not dry and (out / "manifest.json").exists() and not force:
        log(f"{week} : déjà fabriquée, en attente de publication — {out}")
        return 0

    base_phrases, base_voix = CAHIER / "phrases.js", CAHIER / "voix-map.js"
    plus = read_js_json(base_phrases, "TROU_PLUS")
    rec = read_js_json(base_voix, "VOIX_REC")
    known = trou_sentences() + [e["s"].replace("___", e["a"]) for e in plus]
    seen = {d_strip(s) for s in known} | set(rec.keys())
    prof = load_profile()
    log(
        f"{week}{' (essai)' if dry else ''} : {n} phrases, niveau {LEVELS[prof['level'] - 1]}, "
        f"sujets {', '.join(prof['domains'])} — {len(plus)} déjà dans phrases.js"
    )

    items, model = generate(
        n, prof, seen, [e["s"].replace("___", e["a"]) for e in plus]
    )
    if len(items) < max(1, n * 3 // 5):
        log(
            f"{week} : seulement {len(items)} phrases valables sur {n} — on s'arrête là"
        )
        return 1

    out.mkdir(parents=True, exist_ok=True)
    clips_dir = out / "clips"
    clips_dir.mkdir(exist_ok=True)
    voiced = []
    for i, e in enumerate(items):
        full = e["s"].replace("___", e["a"])
        wav = clips_dir / f"{i:02d}.wav"
        if tts(full, wav):
            voiced.append((e, wav))
        else:
            log(f"  pas de voix pour : {full[:70]} — phrase écartée")
    if len(voiced) < max(1, n * 3 // 5):
        log(f"{week} : seulement {len(voiced)} phrases dites — on s'arrête là")
        return 1

    shard = f"voix-{code}.mp3"
    entries = build_shard([wav for _, wav in voiced], out / shard, shard)
    new_items, new_rec = [], {}
    for i, ((e, _), seg) in enumerate(zip(voiced, entries)):
        e = {"id": f"n{code.replace('w', '')}{i:02d}", **e, "w": week}
        new_items.append(e)
        new_rec[d_strip(e["s"].replace("___", e["a"]))] = seg
    write_phrases(out / "phrases.js", plus + new_items)
    write_voix(out / "voix-map.js", {**rec, **new_rec})
    manifest = {
        "week": week,
        "code": code,
        "dry": dry,
        "created": dt.datetime.now().isoformat(timespec="seconds"),
        "model": model,
        "voice": {"provider": "cartesia", "model": VOICE_MODEL, "voice_id": VOICE_ID},
        "ids": [e["id"] for e in new_items],
        "shard": shard,
        "base": {"phrases.js": sha256(base_phrases), "voix-map.js": sha256(base_voix)},
        "published": False,
    }
    (out / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    if not dry:
        st["weeks"][week] = {
            "generated": manifest["created"],
            "published": None,
            "n": len(new_items),
        }
        save_state(st)
    log(
        f"{week} : {len(new_items)} phrases dites, piste {shard} "
        f"({(out / shard).stat().st_size // 1024} Ko) — prêt à publier : {out}"
    )
    return 0


def pending() -> Path | None:
    """La plus ancienne semaine fabriquée et pas encore publiée, ou None."""
    for d in sorted(p for p in OUT.glob("20*-W*") if p.is_dir()):
        m = d / "manifest.json"
        if m.exists() and not json.loads(m.read_text(encoding="utf-8")).get(
            "published"
        ):
            return d
    return None


def mark_published(week: str, version: str) -> None:
    out = OUT / week
    m = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
    for f in ("phrases.js", "voix-map.js", m["shard"]):
        shutil.copy2(out / f, CAHIER / f)
    if (out / "index.html").exists():
        shutil.copy2(out / "index.html", CAHIER / "index.html")
    m["published"] = dt.datetime.now().isoformat(timespec="seconds")
    m["version"] = version
    (out / "manifest.json").write_text(
        json.dumps(m, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    st = load_state()
    st["weeks"].setdefault(week, {}).update(
        {"published": m["published"], "version": version}
    )
    save_state(st)
    shutil.rmtree(out / "clips", ignore_errors=True)  # les WAV ne servent plus
    log(
        f"{week} : publiée (version {version}) — miroir le-cahier/ à jour, {len(m['ids'])} phrases"
    )


def profile_from(path: Path | str) -> None:
    """Met à jour profil.json avec ce que l'apprenant a réglé dans Le Profil."""
    d = json.loads(Path(path).read_text(encoding="utf-8"))
    d = d.get("data", d) if isinstance(d.get("data"), dict) else d
    apply_profile(d)


def profile_set(level: int | None, domains: str | None) -> None:
    """Même mise à jour, sans fichier : niveau et sujets donnés en clair.

    Sert quand la session sans surveillance n'a pas pu enregistrer le document.
    Aucun texte libre ne passe par ici — seulement un entier et des clés connues."""
    apply_profile(
        {
            "level": level,
            "profil": {"domains": [x.strip() for x in (domains or "").split(",")]},
        }
    )


def apply_profile(d: dict[str, Any]) -> None:
    prof = load_profile()
    if isinstance(d.get("level"), int) and 1 <= d["level"] <= 6:
        prof["level"] = d["level"]
    p = d.get("profil") or {}
    doms = [x for x in (p.get("domains") or []) if x in DOMAINS]
    if doms:
        prof["domains"] = doms
    for k in ("why", "l1"):
        if isinstance(p.get(k), str) and p[k].strip():
            prof[k] = p[k].strip()[:300]
    prof["updated"] = dt.date.today().isoformat()
    PROFILE.write_text(
        json.dumps(prof, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    log(
        f"profil : niveau {LEVELS[prof['level'] - 1]}, sujets {', '.join(prof['domains'])}"
    )


def selftest() -> int:
    """dStrip doit donner exactement les clés de la carte d'origine (40 phrases)."""
    rec = read_js_json(CAHIER / "voix-map.js", "VOIX_REC")
    legacy = {k for k, v in rec.items() if len(v) == 2}
    keys = {d_strip(s) for s in trou_sentences()}
    missing = legacy - keys
    print(
        f"{len(keys)} phrases du socle, {len(legacy)} clés d'origine, {len(missing)} sans correspondance"
    )
    for k in sorted(missing)[:5]:
        print("  ", k)
    return 0 if not missing else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--n", type=int, default=20)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--pending", action="store_true")
    ap.add_argument("--print", action="store_true")
    ap.add_argument("--mark-published")
    ap.add_argument("--version", default="?")
    ap.add_argument("--profile-from")
    ap.add_argument("--profile-set", action="store_true")
    ap.add_argument("--level", type=int)
    ap.add_argument("--domains")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if a.pending:
        p = pending()
        if p and a.print:
            print(p)
        return 0 if p else 1
    if a.mark_published:
        mark_published(a.mark_published, a.version)
        return 0
    if a.profile_from:
        profile_from(a.profile_from)
        return 0
    if a.profile_set:
        profile_set(a.level, a.domains)
        return 0
    try:
        return run(max(1, min(40, a.n)), a.dry_run, a.force)
    except Exception as e:  # le log doit dire ce qui a cassé
        log(f"ÉCHEC : {type(e).__name__} : {str(e)[:300]}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
